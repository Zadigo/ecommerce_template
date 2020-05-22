try:
    import stripe
except ImportError:
    print('You should install Stripe in order to use the payment logic.')
import datetime
import os
import re
import secrets
from urllib import parse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.core.serializers import serialize
from django.http.response import JsonResponse
from django.shortcuts import redirect, reverse

from shop import models

try:
    from accounts.models import MyAnonymousUser
except:
    USER = get_user_model()


def create_payment_reference(n=5):
    """Create a basic reference: `NAW201906126011b0e0b8`
    """
    current_date = datetime.datetime.now().date()
    prefix = f'NAW{current_date.year}{current_date.month}{current_date.day}'
    return prefix + secrets.token_hex(n)

def convert_debug():
    """Helper that gets the environment variable DEBUG and
    helps return the correct mode for actions.

    This converter does not take into account the DEBUG setting
    in the settings file since in production mode, the DEBUG setting
    is set with the environment variable.

    We can then assume that if its not set explicitly or is "True", 
    then we are in development mode.
    """
    debug = os.environ.get('DEBUG')
    if not debug:
        # If debug is not set e.g. none,
        # just return development mode
        development_mode = True
    elif debug is False or debug == 'False':
        # If False, return the
        # production mode
        development_mode = False
    elif debug or debug == 'True':
        # .. development mode
        development_mode = True
    else:
        # In any other cases, just return
        # the safe development mode
        development_mode = True
    return development_mode

def stripe_context_processors(request):
    """Return the publisheable key directly in the context
    of the application
    """
    keys = dict()
    # If DEBUG is True, we are in 
    # development return the test key
    if convert_debug():
        keys.update({'publishable_key': 'pk_test_eo8zzqww6iuVFzWmLQEJ4F7K'})
        return keys
    else:
        keys.update({'publishable_key': 'pk_live_5skKfskQRtjARTMQpVxzGsH9'})
        return keys

def initialize_stripe(keys:dict):
    """Initialize stripe is a way that can better evaluate in what
    mode and with which key we are working in a given environment.
    """
    if not 'test' and 'live' in keys:
        msg = 'Dict should have a test and live key'
        return {'Error': msg}

    if convert_debug():
        stripe.api_key = keys['test']
        stripe_mode = 'Development'
    else:
        stripe.api_key = keys['live']
        stripe_mode = 'Production'
    return {'stripe_mode': stripe_mode}

stripe_mode = initialize_stripe({'test': 'sk_test_QkRv7ivfBRfQZiYzIfsOTd68', 'live': 'sk_live_GpShUMmBw626p8otQ89Pl3qg'})

class StripeCharge:
    """A wrapper class that objectifies the stripe charge in order
    to perform other actions on the response.

    Description
    -----------
    """
    def __init__(self, charge: dict):
        self.charge = charge
    
    @property
    def id(self):
        return self.charge['id']

    @property
    def amount(self):
        return self.charge['amount']

    @property
    def billing_details(self):
        return self.charge['billing_details']

    @property
    def status(self):
        return self.charge['status']

    @property
    def is_successful(self):
        return self.charge['status'] == 'success'

class UserInfosHelper(dict):
    """A class that simplifies retrieving of data
    from payment user form POST request"""
    def __init__(self, request, **kwargs):
        self.internal_dict = {}
        self.key_errors = []

        if isinstance(request, WSGIRequest):
            post_data = request.POST.dict().copy()
            post_data.pop("csrfmiddlewaretoken")

            required_fields = ['email', 'telephone', 'address', 
                                    'city', 'zip_code', 'shipping', 'country']
            optional_fields = ['name', 'firstname', 'lastname', \
                                    'billing_equals_shipping', 'save_for_next_time']

            for key, value in self.internal_dict.items():
                if isinstance(value, list):
                    value = value[0]
                self.internal_dict.update({key: value})

            for field in required_fields:
                if field not in self.internal_dict:
                    try:
                        self.internal_dict.update({field: post_data[field]})
                    except KeyError:
                        self.key_errors.append(field)
                        if field == 'shipping':
                            self.internal_dict.update({field: 'standard'})
                        else:
                            self.internal_dict.update({field: None})

            for field in optional_fields:
                if field in post_data:
                    if field == 'billing_equals_shipping' \
                            or field == "save_for_next_time":
                        if field == 'on':
                            self.internal_dict.update({'methods': {field: True}})
                        elif field == 'off':
                            self.internal_dict.update({'methods': {field: False}})

                    if field == 'firstname' \
                            or field == 'lastname' \
                                or field == 'name':
                        self.internal_dict.update({field: post_data[field]})
                else:
                    self.key_errors.append(field)
        else:
            self.key_errors.append({'request_error': 'Is not a valid WSGI request'})

    def __repr__(self):
        return str(self.internal_dict)

    def __str__(self):
        return self.__repr__()

    @property
    def get_user_infos(self):
        import json
        items = str(self.internal_dict).replace("\'", "\"")
        return f'{json.loads(items)}'

    @property
    def field_errors(self):
        return f'FieldErrors({self.key_errors})'

class ProcessPayment:
    """The main logic that initiates and processes a Stripe
    payment

    Description
    -----------

        Once the token is received from JS, this logic interracts
        with the databases and does a series of other validations
        in order to initiate the payment

    Parameters
    ----------

        Request: the HTTP request

        Stripe_token: the tokenized version of the card the user has
        entered for the payment

        User_infos: additional user information for tracking purposes

        Substitute_user_mode_to: a model to use if you wish to substitute
        the user model to another one. The model should have the following
        fields:
            - cart_id,
            - email
            - address
            - telephone
            - country
            - zip_code

        Cart_url / cart_success / login_url: urls to use in order to direct
        the user to the correct pages
    """
    cart_url = '/shop/cart'
    cart_success = '/shop/cart/success'
    login_url = '/accounts/login'
    substitute_user_model_to = None

    def __init__(self, request, stripe_token, user_infos: dict):
        self.base_response = {
            'status': None,
            'redirect_url': None
        }

        self.stripe_token = stripe_token

        # Check that the user information have all the
        # required fields in order to prevent KeyError
        # below when referencing to these fields
        self.user_infos = self._check_user_infos(user_infos)

        self.request = request

        # Create a reference for the
        # order here
        self.order_reference = create_payment_reference()

        self.total_of_products_to_buy = 0

        # This parameter returns an charge
        # object that can be used for other
        # kinds of processing afterwards
        self.completed_charge = None

        # Access the user once the payment
        # process has been done
        self.anonymous_user = None

    def fake_payment_response(self, reason=None, success='success', redirect=False):
        """This simulates the payment process by returning either
        an error dictionnary or a successful one. This is a standalone
        method created to facilitate testing on the frontend"""
        base_response = {
            'reason': reason,
            'success': success
        }
        if redirect:
            base_response['redirect_url'] = self.cart_success
        else:
            base_response['redirect_url'] = False
        return JsonResponse(data=base_response, safe=True, status=200, content_type='json')


    def payment_processor(self, customer_id=None, payment_debug_mode=False, **kwargs):
        """Process a payment and get the charge as an object
        for further processing.

        Parameters
        -----------

            Customer_id: a valid customer ID to use in order
            to link a payment to a registered customer in Stripe
        """
        total_of_products_to_buy = 0

        if self.stripe_token is None:
            self.base_response.update(
                {
                    'status': 400,
                    'redirect_url': self.cart_url,
                    'reason': 'Stripe does not exist.'
                }
            )
            return self.json_response()

        # Get the cart iD from the session 
        # and if it is none, then return 0
        # because the user has nothing to
        # pay for
        cart_id = self.request.session.get('cart_id')
        cart_id = 'fake_cart_id'
        if cart_id:
            # TODO: The model tries to get a get_cart_total() on the model
            # from a cart_manager() model manager. It should return the total
            # sum of items that should be charged to Stripe
            total_of_products_to_buy = models.Cart.cart_manager.cart_total(cart_id)
        else:
            self.base_response.update(
                {
                    'status': 500,
                    'reason': 'Cart missing.'
                }
            )
            return self.json_response()

        if total_of_products_to_buy != 0:
            amount = self.price_to_stripe(total_of_products_to_buy)
            # Now we can create the dict that will be used
            # to process the payment -- In this case, we do
            # need the customer_id for now since we are not
            # registering customers to charge.
            # We just need their card.
            params = {
                'amount': amount,
                'currency': 'eur',
                'source': self.stripe_token,
                'description': 'This is an order for cart %s' % cart_id,
                'receipt_email': self.user_infos['email'],
                'shipping': {
                    'address': {
                        'line1': self.user_infos['address'],
                        'city': self.user_infos['city'],
                        'postal_code': self.user_infos['zip_code']
                    },
                    'name': 'Clothes',
                    'phone': self.user_infos['telephone']
                },
                'metadata': {
                    'name': f'{self.user_infos["firstname"]} {self.user_infos["lastname"]}',
                    'order_reference': self.order_reference,
                    'shipping': self.user_infos['shipping']
                }
            }

            if 'tracking_number' in kwargs and \
                    'carrier' in kwargs:
                params.update(
                    {
                        'tracking_number': kwargs['shipping']['tracking_number'],
                        'carrier': kwargs['shipping']['carrier']
                    }
                )
            
            if customer_id:
                params.update({'customer': customer_id})

            if not payment_debug_mode:
                # There we create the charge which should
                # contain 'succeeded' in order to proceed
                charge = stripe.Charge.create(**params)
            else:
                # A simple dict that passes the payment
                # as successful in order order to debug
                # the rest of the payment process
                print('[LOGIC]: Debugging payment')
                charge = {'status': 'succeeded'}
            
            if charge['status'] == 'succeeded':
                parameters = parse.urlencode(
                    {
                        'order': self.order_reference.lower(),
                        'transaction': charge['id']
                    }
                )
                # If the payment was successful,
                # then we can redirect the user
                # to the success page
                url = f'/shop/cart/success-page?{parameters}'

                # We can mark the products as paid
                # so that we can proceed to sending
                # them the customer

                # And then create and anonymous customer
                # so that we can keep track from our
                # admin interface
                self.anonymous_user = self._create_anonymous_user(cart_id)
                # Now associate the products to the user
                products.update(user=self.anonymous_user)

                # Now we can create the order in our
                # database for each product that was
                # paid for by the customer
                # item = self.update_model('', '', '', field='field')

                # Now this is the response that will be returned
                # to the AJAX function that called to process
                self.base_response.update(
                    {
                        'status': 200,
                        'redirect_url': url,
                        'order_reference': self.order_reference
                    }
                )

                # We are sure there is a cart_id but just
                # in case protect us against any given error
                self.request.session.pop('cart_id')
                # Delete the products that
                # the user placed in the cart
                # products.delete()
                # Or, mark these products as
                # payed_for in the database -;
                # we can then use a later cron
                # do delete these products when
                # the database becomes a little
                # bit too full

        else:
            # Just return some sort of
            # error response
            self.base_response.update(
                {
                    'status': 500,
                    'redirect_url': '/shop/cart/',
                    'order_reference': self.order_reference
                }
            )
            return {}

        return StripeCharge(charge)

    def json_response(self):
        """Get a valid response for Django view in relation
        to the payment
        """
        status = self.base_response['status']
        return JsonResponse(self.base_response, safe=False, status=status, content_type='json')

    def classic_http_response(self, viewname=None):
        """Returns a none AJAX response by redirecting 
        to a viewname or a given path"""
        if viewname:
            return redirect(reverse(viewname))
        return redirect

    @property
    def rest_framework_response(self):
        """Return a valid response from the rest framework library"""
        try:
            from rest_framework.response import Response
        except ImportError:
            return self.json_response()
        self.base_response['success'] = 'success'
        return Response(data=self.base_response, status=200)

    def _create_customer(self):
        """This function can used in order to create a customer
        in Stripe before or during the payment process
        """
        pass

    def _create_anonymous_user(self, cart_id):
        """Create an anonymous user in our database for marketing and remarketing
        reasons. This also serves as a way to keep a link between the products that
        were ordered and the customer
        """
        data = {
            'cart': cart_id,
            'email': self.user_infos['email'],
            'address': self.user_infos['address'],
            # 'telephone': self.user_infos['telephone']
            'country': self.user_infos['country'],
            'zip_code': self.user_infos['zip_code']
        }
        # user = USER.objects.get_or_create(**data)
        # user = MyAnonymousUser.objects.get_or_create(**data)
        user = MyAnonymousUser.objects.create(**data)
        return user

    def cleaned_data(self, email, telephone):
        email = re.match(r'^\w+(?:\.|\-\_)?\w+\@\w+\.\w+$', email)
        telephone = re.match(r'^(\+\d{1,2})?(\d{10})$', telephone)

    @staticmethod
    def price_to_stripe(price):
        """A defintion that converts a decimal into a
        Stripe formatted number

        Example
        -------
            
            12.95€ should be 1295 for Stripe
        """
        return int(price * 100)

    @staticmethod
    def _check_user_infos(user_infos: dict):
        """Checks whether some parameters are present in the
        dictionnary that was passed. If not, proceeds to update
        that dictionnary with the missing values marked as None

        Description
        -----------

            A base dictionary should have the following pieces
            of information:

                {
                    email: 
                    address:
                    city:
                    zip_code:
                    shipping:
                }
        """
        if 'name' not in user_infos \
                or 'lastname' not in user_infos \
                    and 'firstname' not in user_infos:
            user_infos.update({'firstname': None, 'lastname': None})

        if 'email' not in user_infos:
            user_infos.update({'email': None})

        if 'telephone' not in user_infos:
            user_infos.update({'telephone': None})

        if 'address' not in user_infos:
            user_infos.update({'address': None})

        if 'city' not in user_infos:
            user_infos.update({'city': None})

        if 'zip_code' not in user_infos:
            user_infos.update({'zip_code': None})

        if 'shipping' not in user_infos:
            user_infos.update({'shipping': 'standard'})

        if 'shipping' in user_infos:
            if user_infos['shipping'] == '' or \
                    user_infos['shipping'] is None:
                user_infos.update({'shipping': 'standard'})

        if 'country' not in user_infos:
            user_infos.update({'country': 'France'})

        return user_infos

    def payment_processor_with_model_update(self, model, item_id, item_value, \
                        customer_id=None, payment_debug_mode=False, **kwargs):
        """Updates a given model which would most probably be
        your Orders model. The model should have a paid for field
        that marks an order as completed"""
        from django.core.exceptions import FieldDoesNotExist
        charge = self.payment_processor(customer_id=customer_id, \
                            payment_debug_mode=payment_debug_mode, **kwargs)
        if charge.is_successful:
            item = model.objects.get(**{item_id: item_value})
            if item:
                try:
                    item.payed_for = True
                except FieldDoesNotExist:
                    return False
                else:
                    item.save()
                return item
            return False
        else:
            self.base_response.update(
                {
                    'status': 500,
                    'redirect_url': self.cart_success,
                    'order_reference': self.order_reference,
                    'reason': 'Payment successful. Model failed.'
                }
            )
            return self.json_response()
