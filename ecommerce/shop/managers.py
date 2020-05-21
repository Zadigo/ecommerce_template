from django.db.models import Count, F, QuerySet, Sum
from django.core import exceptions
from shop import utilities
from django.db.models import fields


class ImageManager(QuerySet):
    pass

class CollectionManager(QuerySet):
    pass

class ProductManager(QuerySet):
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
        return self.filter(cart_id__exact=cart_id)

    def cart_products(self, cart_id):
        constructed_products = []
        products = self.my_cart(cart_id)
        for product in products:
            related_products = product.product.all()
            for related_product in related_products:
                constructed_products.append({
                    'id': related_product.id,
                    'name': related_product.name,
                    # 'description': related_product
                    'price_ht': product.price_ht,
                    'total': product.price_ht * product.quantity,
                    'quantity': product.quantity,
                    'url': related_product.get_main_image_url
                })
        return constructed_products

    def cart_total(self, cart_id):
        """Returns the total of the cart"""
        cart = self.my_cart(cart_id)
        combined_expression = F('price_ht') * F('quantity')
        # {cart_total: ...}
        return cart.aggregate(cart_total=Sum(combined_expression, output_field=fields.DecimalField()))

    def number_of_products(self, cart_id):
        return self.my_cart(cart_id).aggregate(Sum(F('quantity')))

    def add_to_cart(self, request, current_product):
        cart_id = request.session.get('cart_id')
        quantity = request.POST.get('quantity')

        if not cart_id:
            pass

        if not quantity:
            quantity = 1

        if not cart_id:
            # In the case there was no cart id
            # in the session, just create a new
            # cart all togther for the customer
            cart_id = utilities.create_cart_id()
            details = {
                'cart_id': cart_id,
                'price_ht': current_product.price_ht,
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
                    'quantity': int(quantity),
                    'anonymous': True
                }
                new_cart = self.create(**details)
                new_cart.product.add(current_product)
                return new_cart
            else:
                cart.price = current_product.price_ht
                cart.product.add(current_product)
                cart.quantity = F('price_ht') + int(quantity)
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