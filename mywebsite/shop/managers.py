import datetime
import re

from django import http
from django.contrib import messages
from django.core import exceptions
from django.db.models import (Avg, Case, Count, F, Q, QuerySet, Sum, When,
                              fields)
from django.db.models.functions import TruncMonth

from shop import utilities


class CollectionManager(QuerySet):
    def active_products(self, collection_name):
        collection = self.get(name__iexact=collection_name)
        return collection.product_set.filter(active=True)

    def products_between_price(self, collection_name, a, b):
        products = self.active_products(collection_name)
        price_between_a_and_b = Q(price_ht__gt=a) & Q(price_ht__lt=b)
        return products.filter(price_between_a_and_b)


class ProductManager(QuerySet):
    def active_products(self):
        return self.filter(active=True, private=False)

    def private_products(self):
        return self.filter(private=True)
        
    def count_products_by_collection(self):
        """Returns the count of products by collection"""
        products = self.values('collection__name')
        items = products.annotate(count_of=Count('name'))
        return [[item['collection__name'] for item in items], [item['count_of'] for item in items]]

    def average_price_by_collection(self):
        """Returns the average price by collection"""
        products = self.values('collection__name')
        return products.order_by('collection__name')\
                        .annotate(average_price=Count('price_ht'))

    def search_product(self, searched_item):
        """
        Allows the user to search for a product on
        the website
        """
        qfunctions = Q(name__icontains=searched_item) | Q(
            collection__name__icontains=searched_item)
        queryset = self.filter(qfunctions).filter(active=True)
        if queryset.exists():
            return queryset
        return []

    def advanced_search(self, searched_terms):
        """
        This is an advanced search feature for the dashboard
        for example
        """
        queryset = self.all()

        if ':' in searched_terms:
            key, value = searched_terms.split(':')
            if key == 'state':
                if value == 'actif' \
                    or value == 'true' \
                        or value == 'True':
                    return queryset.filter(active=True)
                elif value == 'inactif' \
                    or value == 'false' \
                        or value == 'False':
                    return queryset.filter(active=False)

        if searched_terms.startswith('-'):
            searched_terms = re.search(r'^-(?:\s?)(.*)', searched_terms).group(1)
            searched_terms = ~Q(name__icontains=searched_terms) & ~Q(reference__icontains=searched_terms) \
                            & ~Q(collection__name__icontains=searched_terms)
        else:
            searched_terms = Q(name__icontains=searched_terms) | Q(reference__icontains=searched_terms) \
                            | Q(collection__name__icontains=searched_terms)

        return queryset.filter(searched_terms)

    def to_be_published_today(self):
        current_date = datetime.datetime.now()
        products = self.filter(to_be_published_on__date=current_date, active=False)
        return products


class CartManager(QuerySet):
    def my_cart(self, cart_id):
        """
        Returns all the products of a customer's cart
        """
        return self.filter(cart_id__exact=cart_id)

    def cart_products(self, cart_id):
        """
        Returns all the products within a customer's cart but constructed
        for views that require to include if there is a coupon
        associated to one or many products in the cart
        """
        constructed_products = []

        cart = self.my_cart(cart_id=cart_id).prefetch_related('product')
        product_marked_as_discounted = Q(product__discounted_price__gt=0) & Q(product__discounted=True)
        condition = When(product_marked_as_discounted, then='product__discounted_price')
        annotated_cart = cart.annotate(true_price=Case(condition, default='product__price_ht'))

        try:
            coupon_value = annotated_cart.first().coupon.value
            coupon_code = annotated_cart.first().coupon.code
        except:
            coupon_value = 0
            coupon_code = ''

        for item in annotated_cart:
            # Product that is related to the cart
            # in the Product model
            related_product = item.product
            constructed_products.append(
                {
                    'cart_id': item.id,
                    'product_id': related_product.id,
                    'name': related_product.name,
                    'price_ht': item.true_price,
                    'total': item.true_price * item.quantity,
                    'quantity': item.quantity,
                    'url': related_product.get_main_image_url,
                    'is_discounted': related_product.is_discounted
                }
            )        
        return {'constructed_products': constructed_products,
                        'coupon_value': coupon_value, 'coupon_code': coupon_code}

    def cart_total(self, cart_id, get_queryset=False):
        """
        Total of a customer's cart
        """
        cart = self.my_cart(cart_id)
        # Since we have two different prices (price_ht, discounted_price),
        # determine which price to use when computing the total
        discounted_price_times_quantity = F('product__discounted_price') * F('quantity')
        price_ht_times_quantity = F('product__price_ht') * F('quantity')

        product_marked_as_discounted = Q(product__discounted_price__gt=0) & Q(product__discounted=True)
        first_case = When(product_marked_as_discounted, then=discounted_price_times_quantity)
        case = Case(first_case, default=price_ht_times_quantity, output_field=fields.DecimalField())
        true_price_queryset = cart.annotate(true_price=case)
        
        return true_price_queryset if get_queryset else true_price_queryset.aggregate(cart_total=Sum('true_price'))

    def cart_total_discount_entire_order(self, cart_id):
        """
        This calculates the total price of a cart based
        on whether the cart has coupon and that it is
        applicable on the entire order
        """
        queryset = self.my_cart(cart_id)

        total_discounted_with_coupon = F('true_price') / (F('coupon__value') * (1 - F('coupon__value') / 100))
        total_minus_coupon = F('true_price') - F('coupon__value')

        coupon_is_for_entire_order = Q(coupon__isnull=False) & Q(coupon__on_entire_order=True)
        coupon_on_entire_order_percentage = coupon_is_for_entire_order & Q(coupon__value_type='percentage')
        coupon_on_entire_order_value = coupon_is_for_entire_order & Q(coupon__value_type='fixed amount')

        first_case = When(coupon_on_entire_order_percentage, then=total_discounted_with_coupon)
        second_case = When(coupon_on_entire_order_value, then=total_minus_coupon)

        case = Case(first_case, second_case, default='true_price', output_field=fields.DecimalField())

        return queryset.annotate(reduced_price=case)

    def discount_on_specific_collection(self):
        """
        Calculates the specific discounted price of a product
        based on whether the coupon applies to the collection
        in which in the product is a part of
        """
        # product_is_part_of_collection = None
        # coupon_on_collection_percentage = Q(coupon__isnull=False) & Q(coupon__collection=True) & Q(value_type='percentage')
        # coupon_on_collection_value = Q(coupon__isnull=False) & Q(coupon__collection=True) & Q(value_type='fixed amount')

        # third_case = When(coupon_on_collection_percentage, then=total_discounted_with_coupon)
        # fourth_case = When(coupon_on_collection_value, then=total_minus_coupon)

        pass

    def number_of_products(self, cart_id):
        """Number of products in a cart"""
        return self.my_cart(cart_id).aggregate(Sum('quantity'))

    def add_to_cart(self, request, current_product, enforce_color=False):
        cart_id = request.session.get('cart_id')
        quantity = request.POST.get('quantity')
        color = request.POST.get('color')
        size = request.POST.get('size')

        if not current_product.active:
            messages.error(request, "Une erreur s'est produite - ADD-NA", extra_tags='alert-danger')
            return False

        if color is None:
            messages.error(request, "Une erreur s'est produite - ADD-CO", extra_tags='alert-danger')
            # If variant is empty,
            # just raise an error by refusing
            # the request to the database
            return False

        if size is None:
            size = ''

        if quantity is None:
            quantity = 1

        if not cart_id:
            # In the case there was no cart id
            # in the session, just create a new
            # cart all togther for the customer
            cart_id = utilities.create_cart_id()
            details = {
                'cart_id': cart_id,
                'price_ht': current_product.get_price(),
                'size': size,
                'color': color,
                'quantity': int(quantity),
                'anonymous': True,
                'product': current_product
            }
            try:
                new_cart = self.create(**details)
            except:
                messages.error(request, f"Une erreur s'est produite - ADD-CR", extra_tags='alert-danger')
                return False
            else:
                request.session['cart_id'] = cart_id
                return new_cart
        
        if cart_id:
            try:
                # user_cart = Q(cart_id=cart_id) & Q(product__id=current_product.id)
                # product_details = Q(color=color) 
                # if size:
                #     product_details = product_details & Q(size=size)
                # cart = self.get(user_cart & product_details)
                
                # There might be a cart, but with a different
                # product. In that specific case we need to
                # put a new product in the cart with different
                # quantity
                cart = self.get(cart_id=cart_id, product__id=current_product.id)
            except:
                details = {
                    'cart_id': cart_id,
                    'price_ht': current_product.get_price(),
                    'size': size,
                    'color': color,
                    'quantity': int(quantity),
                    'anonymous': True,
                    'product': current_product
                }
                new_cart = self.create(**details)
                return new_cart
            else:
                cart.price_ht = current_product.price_ht
                cart.product = current_product
                cart.color = color
                cart.size = size
                cart.quantity = F('quantity') + int(quantity)
                cart.anonymous = True
                try:
                    cart.save()
                except:
                    messages.error(request, f"Une erreur s'est produite - ADD-UP", extra_tags='alert-danger')
                    return False
                else:
                    return cart

    def over_thirtee_days(self):
        current_date = datetime.datetime.now().date()
        queryset = self.filter(
            created_on__range=[
                current_date - datetime.timedelta(days=31), current_date
            ]
        )
        return queryset

class DiscountManager(QuerySet):
    def apply_coupon(self, carts, code, total, quantity=0):
        try:
            # The code does not exist, return
            # the total
            discount = self.get(code__iexact=code)
        except:
            return total
        else:
            # Discount should be active. This is
            # a special case where the code is
            # disabled internally
            if not discount.active:
                return total
        
        if discount.usage_limit == 0:
            return total

        if total < discount.minimum_purchase:
            return total

        if quantity > 0 and quantity < discount.minimum_quantity:
            return total

        if discount.start_date <= datetime.datetime.date().now():
            return total

        # Adds the coupon to all the
        # selected carts
        discount.cart_set.set(*list(carts))

        if discount.value_type == 'percentage':
            final_price = total * (1 - discount.value) 
        elif discount.value_type == 'fixed amount':
            final_price = total - discount.value
        elif discount.value_type == 'free shipping':
            pass

        carts.update(discounted_price=final_price)
        




##############
#
# DASHBOARD
#
##############

class BaseStatistics(QuerySet):
    def total_count(self):
        return self.all().count()

class CartsStatisticsManager(BaseStatistics):
    def carts_with_orders(self, return_querysets=False):
        carts = []
        for cart in self.all():
            if cart.customerorder_set.all():
                carts.append(cart)

        if return_querysets:
            return carts

        if carts:
            return len(carts)
        return 0

    def carts_without_orders(self, return_querysets=False):
        carts = []
        for cart in self.all():
            if not cart.customerorder_set.all():
                carts.append(cart)

        if return_querysets:
            return carts

        if carts:
            return len(carts)
        return 0

class OrdersStatisticsManager(BaseStatistics):
    def accepted_orders(self):
        # Orders that are accepted can be counted
        # in the revenue
        return self.filter(accepted=True)

    def non_accepted_orders(self):
        return self.filter(accepted=False)

    def refunded_orders(self):
        """Orders where the customer asked for
        a refund are deducted from revenue
        """
        return self.filter(refund=True)

    def accepted_and_not_refunded(self):
        """Queryset of true revenue of the store"""
        return self.accepted_orders().filter(refund=False)

    def fulfilled_orders(self):
        logic = Q(accepted=True) & Q(completed=True) & Q(refund=False)
        return self.filter(logic)

    def total_refunded_orders(self):
        return self.refunded_orders().aggregate(Sum('payment'))

    def payments_by_month(self):
        queryset = self.annotate(month=TruncMonth('created_on'))
        values = queryset.values('month').annotate(quantity=Count('id'))
                    
        labels = []
        data = []
        for item in values:
            labels.append(item['month'])
            data.append(item['quantity'])
        return [labels, data]

    def latest_orders(self):
        difference = F('created_on') - datetime.timedelta(days=7)
        latest_and_awaiting = Q(created_on__gt=difference) & Q(accepted=False) & Q(completed=False)
        return self.filter(latest_and_awaiting)

    def average_total_order(self):
        carts = self.select_related('cart')
        prices = F('cart__price_ttc') * F('cart__quantity')
        return carts.annotate(average_prices=prices).aggregate(Avg('prices'))

    def revenue(self):
        return self.fulfilled_orders().aggregate(Sum('payment'))

    def awaiting_revenue(self):
        # Orders that were not yet
        # accepted and awaiting to
        # be delivered to the customer
        return self.non_accepted_orders().aggregate(Sum('payment'))

    def profit(self):
        carts = self.prefetch_related('cart')
        profit = F('cart__price_ttc') - F('cart__price_ht')
        total_profit = Sum(profit*F('cart__quantity'), output_field=fields.DecimalField())
        return carts.annotate(total_profit=total_profit).aggregate(Sum('total_profit'))
