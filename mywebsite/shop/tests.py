import ast

from django.contrib.sessions.middleware import SessionMiddleware
from django.db.models import DecimalField
from django.http import JsonResponse
from django.shortcuts import reverse
from django.test import Client, RequestFactory, TestCase

from shop import models, views
from mywebsite import views as base_views

factory = RequestFactory()


class PaymentPage(TestCase):
    def access_payment_page(self):
        response = self.client.get(reverse('paymentt'))
        self.assertEqual(response.status_code, 200)


TEST_PRODUCTS = [
    {
        'name': 'Kendall Jenner Lipstick',
        'description': 'A lipstipck specifically designed for the modern girl',
        'price_ht': 45,
        'slug': 'kendall-academy',
        'active': False
    },
    {
        'name': 'Hailey Baldwin Lipstick',
        'description': 'A lipstipck specifically designed  younger women',
        'price_ht': 25,
        'slug': 'hailey-academy',
        'active': True
    }
]

class ProductModel(TestCase):
    def setUp(self):
        self.test_product = {
            'name': 'Kendall Jenner Lipstick',
            'description': 'A lipstipck specifically designed for the modern girl',
            'price_ht': 45,
            'slug': 'kendall-academy',
            'active': True,
            'collection': create_collection()
        }

    def product_creation(self):
        product = models.Product.objects.create(**self.test_product)

        self.assertIsNotNone(product)
        self.assertEqual(product.name, 'Kendall Jenner Lipstick')
        self.assertEqual(product.active, True)

        # Associate an image to the product
        # product.images.add(name='Lipstick Image')

        # self.assertIn(product.images.values_list('name'), 'Lipstick Image')

    def create_through_collection(self):
        collection = models.ProductCollection.objects.create(name='Lipsticks')
        collection.product_set.create(**self.test_product)
        product = models.Product.objects.get(name='Kendall Jenner Lipstick')
        
        self.assertEqual(product.name, 'Kendall Jenner Lipstick')
        self.assertTrue(product.slug)


# class TestCollectionModel(TestCase):
#     def setUp(self):
#         self.collection = models.ProductCollection. \
#                         objects.create(name='Lip sticks', view_name='lipsticks')

#     def view_name_is_correctly_formatted(self):
#         """
#         When a collection is created, the clean method takes the
#         name of the collection, takes out the space and stores it
#         in the view_name field. Normally there should have no space
#         e.g. my collection -> mycollection
#         """
#         self.assertEqual(self.collection.view_name, 'lipsticks')


def create_collection():
    return models.ProductCollection. \
        objects.create(name='Lip sticks', view_name='lipsticks')


def build_product_url(product):
    return reverse(
        'product',
        args=[
            product.gender,
            # product.collection.view_name,
            'lipsticks',
            product.id,
            product.slug
        ]
    )


class TestViews(TestCase):
    """
    Tests the page located at /shop/collections/femme
    """
    def test_home_page(self): 
        request = factory.get(reverse('home'))
        response = base_views.HeroView.as_view()(request)

    def test_shop_page(self):
        response = self.client.get(reverse('shop'))
        self.assertEqual(response.status_code, 200)

    def test_collections_page(self):
        response = self.client.get(reverse('collection', args=['femme', 'tops']))
        self.assertEqual(response.status_code, 200)

    def test_no_collections_page(self):
        url = reverse('collection', args=['femme', 'cars'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        request = factory.get(url)
        view = views.ProductsView.as_view()(request)
        kwargs = {
            'collection': 'tops'
        }
        view(kwargs)
        self.assertEqual(view, None)

class TestGenderShopView(TestCase):
    """
    Tests the page located at /shop/collections/femme
    """
    def test_access_gender_shop_page(self): 
        response = self.client.get(reverse('shop_gender', args=['femme']))
        self.assertEqual(response.status_code, 200)


class TestProductView(TestCase):
    def setUp(self):
        self.cart_id = None

        collection = create_collection()
        # TODO: The database does not allow the creation of a
        # product if it is not associated to a collection -;
        # does a product necessarily need a collecton or can
        # it just exist on its own?
        products = [models.Product(**{**product, 'collection': collection}) for product in TEST_PRODUCTS]
        models.Product.objects.bulk_create(products)

        self.active_product = models.Product.objects.get(active=True)
        self.inactive_product = models.Product.objects.get(active=False)

        # When the user clicks on the add to cart
        # button, an AJAX request is sent with VueJS
        # to the server in order to add the given
        # product to the cart. The add_to_cart()
        # receives a request which parses this.
        self.factory = RequestFactory()

    def test_access_active_product_page(self):
        """
        Verify that we can access the product page
        """
        response = self.client.get(build_product_url(self.active_product))

        self.assertEqual(response.status_code, 200)
        # The product page passes data for Vue JS. Check that it is
        # present and that it is an array of dicts
        self.assertIn('vue_product', response.context_data.vue_product)
        self.assertIsInstance(response.context_data.vue_product, dict)

    def test_access_non_active_product_page(self):
        """Should generate a 404 page if the product is inactive"""
        response = self.client.get(build_product_url(self.inactive_product))

        self.assertEqual(response.status_code, 404)
    
    def test_add_new_product_to_cart(self):
        """
        This tests the action of putting a product in a cart
        """
        data = {'quantity': 1, 'color': 'rouge', 'size': ''}
        response = self.client.post(build_product_url(self.active_product), data)

        self.assertEqual(response.status_code, 200)

        response_dict = ast.literal_eval(response.getvalue().decode('utf-8'))
        self.assertEqual(response_dict, {'success': 'success'})
        
        # TODO: Get a better way to retrieve
        # the cart or cart id here
        cart = models.Cart.objects.first()
        # We should rename cart_id to
        # something else -; cart reference?
        cart_id = cart.cart_id

        self.assertEqual(str(cart.price_ht), '25.00')
        self.assertEqual(cart.product.name, 'Hailey Baldwin Lipstick')
        self.assertEqual(cart.color, 'rouge')

        self.assertIsNotNone(cart_id)

        total = models.Cart.cart_manager.cart_total(cart_id)
        # This tests that the cart's total is correct. This is critical
        # for when the user decides to checkout.
        self.assertIsInstance(total, dict)
        self.assertDictEqual(total, {'cart_total': DecimalField().to_python('25.00')})

    def test_add_non_active_product_to_cart(self):
        """
        This tests the action of putting a product in a cart when the
        product is not active. Normally, this should never be possible.

        A product is never shown if its not active but it might happen that
        someone post maliciously to a past product that has been deactivated.
        """
        data = {'quantity': 1, 'color': 'rouge', 'size': ''}
        response = self.client.post(build_product_url(self.inactive_product), data)

        self.assertEqual(response.status_code, 500)

    def test_add_new_product_to_cart_no_color(self):
        """
        As a fashion website, color is generally required
        when adding a product to the cart. We don't authorize
        product in a cart if there is no color.
        """
        product = models.Product.objects.filter(active=True)[0]
        data = {'quantity': 1, 'size': ''}
        response = self.client.post(build_product_url(product), data)

        self.assertEqual(response.status_code, 400)

    def add_product_to_existing_cart(self):
        pass

    def mark_a_product_as_liked(self):
        pass


class TestPaymentFunnel(TestCase):
    def test_shipment_page_no_cart(self):
        response = self.client.get(reverse('shipment'))
        self.assertEqual(response.status_code, 302)
        # self.assertIn(response.redirect_chain, '/shop/no-cart')

    def test_shipment_page_with_cart(self):
        session = self.client.session
        session['cart_id'] = 'fake_id'
        session.save()
        request = factory.get(reverse('shipment'))

        self.assertIn(session['cart_id'], 'fake_id')

        views.ShipmentView().setup(request)

        # This section processes the request
        # with the SessionMiddleWare in order
        # to verify that we indeed getting a
        # status code o 200 when accessing
        # this page
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        self.assertEqual(request.session.get('cart_id'), 'fake_id')


# self.request_factory = RequestFactory()

# middleware = SessionMiddleware()
# middleware.process_request(self.request_factory)
# self.request_factory.session.save()




#  factory = RequestFactory()

# session = self.client.session
# session['cart_id'] = 'fake_cart_id'
# session.save()

# request = factory.post(reverse(
#     'product', args=['femme', current_product_viewed.collection.view_name, 
#         current_product_viewed.id, current_product_viewed.slug]))

# response = views.ProductView().setup(request)
