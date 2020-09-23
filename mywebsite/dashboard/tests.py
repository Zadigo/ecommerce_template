from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.test import RequestFactory, TestCase

from dashboard import forms, views
from django.contrib.auth import get_user_model


MYUSER = get_user_model()

def create_and_login():
    credentials = {
        'email': 'pendenquejohn@mail.com',
        'password': 'touparet'
    }
    user = MYUSER.objects.create(**credentials)
    return user, {
        'username': user.email,
        'password': 'touparet'
    }


class TestHomeView(TestCase):
    def test_cannot_go_to_home_page_not_logged_in(self):
        response = self.client.get(reverse('index'), follow=True)
        self.assertEqual(response.get_full_url(), '/')
        self.assertEqual(response.status_code, 200)
    

class TestProdutForm(TestCase):
    def setUp(self):
        self.data = {
            'name': 'My product',
            'description': 'A simple description',
            'sku': '',
            'reference': '',
            'price_pre_tax': 14.5,
            'discount_pct': 0,
            'quantity': 0,
            'in_stock': True,
            'our_favorite': False,
            'discounted': False,
            'active': False,

            'gender': 'femme',
            'price_valid_until': '2020-08-01',
            'collection': 'None',
            'google_category': 'tops',
        }

    def test_can_create_product(self):
        form = forms.ProductForm(data=self.data)
        
        # NOTE: As expected, cannot create a new product without
        # a collection. However, this test forces an item for the
        # collection while the latter does not exis --; on the real
        # website, maybe we should allow creating a product witout
        # it being in a collection?
        self.assertFalse(form.has_error('gender'), msg='gender is not the list')
        self.assertFalse(form.has_error('price_valid_until'), msg='price_valid_until is not the list')
        self.assertFalse(form.has_error('collection'), msg=form.errors.get('collection'))
        self.assertFalse(form.has_error('google_category'), msg='google_category is not the list')

        self.assertTrue(form.is_valid())

    def test_cannot_create_product_with_missing_price(self):
        self.data.update({'price_pre_tax': ''})
        form = forms.ProductForm(data=self.data)
        self.assertTrue(form.has_error('price_pre_tax'))
        with self.assertRaises(TypeError) as ctx:
            print(ctx.msg)


class TestSearchProductview(TestCase):
    def setUp(self):
        user, credentials = create_and_login()
        response = self.client.post('/login/', credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.factory = RequestFactory()
        self.session = self.client.session
        self.user = user
    
    def test_can_do_search(self):
        request = self.factory.get('/dashboard/search/?s=some+product')

        self.session.save()

        request.session = self.session
        request.user = self.user

        view_function = views.SearchView.as_view()
        view = view_function(request)

        self.assertEqual(view.status_code, 200)
