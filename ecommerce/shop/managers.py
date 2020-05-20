from django.db.models import QuerySet
from django.db.models import Sum

class ImageManager(QuerySet):
    pass

class CollectionManager(QuerySet):
    pass

class ProductManager(QuerySet):
    pass

class CartManager(QuerySet):
    def cart_products(self, cart_id=None):
        constructed_products = []
        products = self.all()
        # products = self.filter(cart_id__exact=cart_id)
        for product in products:
            related_products = product.product.all()
            for related_product in related_products:
                constructed_products.append({
                    'name': related_product.name,
                    # 'description': related_product
                    'price_ht': related_product.price_ht,
                    'quantity': product.quantity,
                    'url': related_product.get_main_image_url
                })
        return constructed_products

    def cart_total(self, cart_id):
        """Returns the total of the cart"""
        cart = self.all()
        return cart.aggregate(Sum('product__price_ht'))

class OrdersManager(QuerySet):
    pass

class ShipmentManager(QuerySet):
    pass