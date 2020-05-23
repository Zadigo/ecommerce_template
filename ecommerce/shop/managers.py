from django import http
from django.core import exceptions
from django.db.models import Case, Count, F, Q, QuerySet, Sum, When, fields
from django.db.models.functions import TruncMonth
import datetime
from shop import utilities


class ImageManager(QuerySet):
    pass

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

class CartManager(QuerySet):
    def my_cart(self, cart_id):
        """Returns a cart"""
        return self.filter(cart_id__exact=cart_id)

    def cart_products(self, cart_id):
        """Returns all the products within a customer's cart"""
        constructed_products = []

        cart = self.my_cart(cart_id=cart_id).prefetch_related('product')
        # Get the real prices of the product
        condition = When(product__discounted_price__gt=0, then='product__discounted_price')
        annotated_cart = cart.annotate(true_price=Case(condition, default='product__price_ht'))

        try:
            coupon_value = annotated_cart.first().coupon.value
            coupon_code = annotated_cart.first().coupon.code
        except:
            coupon_value = 0
            coupon_code = ''

        for product in annotated_cart:
            # Product that is related to the cart
            # in the Product model
            related_product = product.product.get()
            constructed_products.append(
                {
                    'cart_id': product.id,
                    'product_id': related_product.id,
                    'name': related_product.name,
                    'price_ht': product.true_price,
                    'total': product.true_price * product.quantity,
                    'quantity': product.quantity,
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
        
        first_case = When(product__discounted_price__gt=0, then=discounted_price_times_quantity)
        case = Case(first_case, default=price_ht_times_quantity, output_field=fields.DecimalField())
        true_price_queryset = cart.annotate(true_price=case)

        return true_price_queryset.aggregate(cart_total=Sum('true_price'))
    
    def number_of_products(self, cart_id):
        """Number of products in a cart"""
        return self.my_cart(cart_id).aggregate(Sum(F('quantity')))

    def add_to_cart(self, request, current_product):
        """Add or increase the amount of products in a given cart"""
        cart_id = request.session.get('cart_id')

        products_without_size = ['sacs']

        quantity = request.POST.get('quantity')
        color = request.POST.get('color')
        size = request.POST.get('size')

        if color is None:
            # If this variant is empty,
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
                'price_ht': current_product.price_ht,
                'size': size,
                'color': color,
                'quantity': int(quantity),
                'anonymous': True
            }
            new_cart = self.create(**details)
            new_cart.product.add(current_product)
            request.session['cart_id'] = cart_id
            return new_cart
        
        if cart_id:
            try:
                # There might be a cart, but with a different
                # product. In that specific case we need to
                # put a new product in the cart with different
                # quantity
                cart = self.get(cart_id=cart_id, product__id=current_product.id)
            except:
                details = {
                    'cart_id': cart_id,
                    'price_ht': current_product.price_ht,
                    'size': size,
                    'color': color,
                    'quantity': int(quantity),
                    'anonymous': True
                }
                new_cart = self.create(**details)
                new_cart.product.add(current_product)
                new_cart.anonymous = True
                new_cart.save()
                return new_cart
            else:
                cart.price = current_product.price_ht
                cart.product.add(current_product)
                cart.color = color
                cart.size = size
                cart.quantity = F('quantity') + int(quantity)
                cart.anonymous = True
                cart.save()
                return cart

class OrdersManager(QuerySet):
    pass

class ShipmentManager(QuerySet):
    pass

class FormsManager(QuerySet):
    def for_forms(self):
        choices = []
        queryset = self.all()
        for name in queryset:
            choices.append([name, name])
        return choices



class CollectionStatisticsManager(QuerySet):
    """For dashboard"""
    pass

class ProductStatisticsManager(QuerySet):
    """For dashboard"""
    def total_count(self):
        return self.all().count()


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

    def revenue(self):
        carts = self.select_related('cart')
        cart_total = Sum(F('cart__price_ht')*F('cart__quantity'), output_field=fields.DecimalField())
        return carts.annotate(revenue=cart_total).aggregate(Sum('revenue'))