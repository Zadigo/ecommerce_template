import datetime

from django import http
from django.contrib import messages
from django.core import exceptions
from django.db.models import (Avg, Case, Count, F, Q, QuerySet, Sum, When,
                              fields)
from django.db.models.functions import TruncMonth

from shop import models, utilities


class ImageManager(QuerySet):
    def images_for_forms(self):
        images = self.values_list('name', flat=True)
        return [(image, image) for image in images]

class CollectionManager(QuerySet):
    def active_products(self, collection_name):
        collection = self.get(name__iexact=collection_name)
        return collection.product_set.filter(active=True)

    def products_between_price(self, collection_name, a, b):
        products = self.active_products(collection_name)
        price_between_a_and_b = Q(price_ht__gt=a) & Q(price_ht__lt=b)
        return products.filter(price_between_a_and_b)

class ProductManager(QuerySet):
    def product_colors(self, product_id):
        """Gets the available colors for a product"""
        colors = self.get(id=product_id).images.values_list('variant', flat=True)
        return list(set(colors))

    def count_products_by_collection(self):
        """Returns the count of products by collection"""
        products = models.Product.objects.values('collection__name')
        items = products.annotate(count_of=Count('name'))
        return [[item['collection__name'] for item in items], [item['count_of'] for item in items]]

    def average_price_by_collection(self):
        """Returns the average price by collection"""
        products = models.Product.objects.values('collection__name')
        return products.order_by('collection__name')\
                        .annotate(average_price=Count('price_ht'))

    def search_product(self, searched_item):
        qfunctions = Q(name__icontains=searched_item) | Q(collection__name__icontains=searched_item)
        queryset = self.filter(qfunctions).filter(active=True)
        if queryset.exists():
            return queryset
        return []

class CartManager(QuerySet):
    def my_cart(self, cart_id):
        """Returns a cart"""
        return self.filter(cart_id__exact=cart_id)

    def cart_products(self, cart_id):
        """Returns all the products within a customer's cart"""
        constructed_products = []

        cart = self.my_cart(cart_id=cart_id).prefetch_related('product')
        # Get the real prices of the product
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
                    'url': related_product.images.all().first().url,
                    'is_discounted': related_product.is_discounted()
                }
            )        
        return {'constructed_products': constructed_products,
                        'coupon_value': coupon_value, 'coupon_code': coupon_code}

    def cart_total(self, cart_id):
        """Total of a customer's cart"""
        cart = self.my_cart(cart_id)
        # Since we have two different prices (price_ht, discounted_price),
        # determine which price to use when computing the total
        discounted_price_times_quantity = F('product__discounted_price') * F('quantity')
        price_ht_times_quantity = F('product__price_ht') * F('quantity')
        
        product_marked_as_discounted = Q(product__discounted_price__gt=0) & Q(product__discounted=True)
        first_case = When(product_marked_as_discounted, then=discounted_price_times_quantity)
        case = Case(first_case, default=price_ht_times_quantity, output_field=fields.DecimalField())
        true_price_queryset = cart.annotate(true_price=case)

        return true_price_queryset.aggregate(cart_total=Sum('true_price'))
    
    def number_of_products(self, cart_id):
        """Number of products in a cart"""
        return self.my_cart(cart_id).aggregate(Sum(F('quantity')))

    def add_to_cart(self, request, current_product):
        cart_id = request.session.get('cart_id')
        quantity = request.POST.get('quantity')
        color = request.POST.get('color')
        size = request.POST.get('size')

        if not current_product.active:
            return False

        if color is None:
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
                messages.error(request, f"Une erreur s'est produite - CXCRE", extra_tags='alert-danger')
                return False
            else:
                request.session['cart_id'] = cart_id
                return new_cart
        
        if cart_id:
            try:
                # TODO
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
                try:
                    cart.price_ht = current_product.price_ht
                    cart.product = current_product
                    cart.color = color
                    cart.size = size
                    cart.quantity = F('quantity') + int(quantity)
                    cart.anonymous = True
                    cart.save()
                except:
                    messages.error(request, f"Une erreur s'est produite - CXAD", extra_tags='alert-danger')
                    return False
                else:
                    return cart


# For Dashboard

class BaseStatistics(QuerySet):
    def total_count(self):
        return self.all().count()

class CartsStatisticsManager(BaseStatistics):
    pass

class OrdersStatisticsManager(BaseStatistics):
    def total_payments(self):
        return self.aggregate(total_payments=Sum('payment'))

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
        return self.filter(created_on__gt=difference)

    def average_total_order(self):
        carts = self.select_related('cart')
        prices = F('cart__price_ttc') * F('cart__quantity')
        return carts.annotate(average_prices=prices).aggregate(Avg('prices'))

    def revenue(self):
        return self.aggregate(Sum('payment'))

    def profit(self):
        carts = self.prefetch_related('cart')
        profit = F('cart__price_ttc') - F('cart__price_ht')
        total_profit = Sum(profit*F('cart__quantity'), output_field=fields.DecimalField())
        return carts.annotate(total_profit=total_profit).aggregate(Sum('total_profit'))
