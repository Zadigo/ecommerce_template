import datetime
import os
import secrets
from urllib.parse import urlencode

from django.core import exceptions
from django.core.handlers.wsgi import WSGIRequest

try:
    import stripe
except ImportError:
    print('You should install Stripe in order to use the payment logic.')
    raise

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




def create_payment_reference(n=5):
    """Create a basic reference: `NAW201906126011b0e0b8`
    """
    current_date = datetime.datetime.now().date()
    prefix = f'NAW{current_date.year}{current_date.month}{current_date.day}'
    return prefix + secrets.token_hex(n)

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

class BasePaymentBackend:
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

    cart_model = None
    cart_success = '/shop/cart/success'

    def __init__(self, request, stripe_token, user_infos:dict):
        self.stripe_token = stripe_token

        # Check that the user information have all the
        # required fields in order to prevent KeyError
        # below when referencing to these fields
        # self.user_infos = self._check_user_infos(user_infos)

        self.request = request

        # Create a reference for the
        # order here
        self.order_reference = create_payment_reference()

        self.total_of_products_to_buy = 0

        # This parameter returns a charge
        # object that can be used for other
        # kinds of processing afterwards
        self.completed_charge = None

        # Access the user once the payment
        # process has been done
        self.anonymous_user = None

        # The final url to send
        # the user to
        self.final_url = None

        self.errors = []

        self.user_infos = self._check_user_infos(user_infos)

        self.cart_queryset = None

    def process_payment(self, customer_id=None, payment_debug_mode=False, **kwargs):
        """Process a payment and get the charge as an object
        for further processing.

        Parameters
        -----------

            Customer_id: a valid customer ID to use in order
            to link a payment to a registered customer in Stripe
        """
        total_of_products_to_buy = 0

        if self.stripe_token is None:
            self.errors.append('No token')
            return False

        # Get the cart iD from the session 
        # and if it is none, then return 0
        # because the user has nothing to
        # pay for
        cart_id = self.request.session.get('cart_id')

        if cart_id:
            if self.cart_model is None:
                self.errors.append('No cart model')
                raise exceptions.ImproperlyConfigured('You should provide a model from which \
                we can extract the cart total.')
            try:
                # The model tries to get the cart
                self.cart_queryset = self.cart_model.objects.filter(cart_id__iexact=cart_id).first()
                # The model tries to get a get_cart_total() on the model
                # from a cart_manager() model manager. It should return the total
                # sum of items that should be charged to Stripe
                total_of_products_to_buy = self.cart_model.cart_manager.cart_total(cart_id)
            except:
                self.errors.append('Manager with cart total does not exist')
                raise exceptions.ObjectDoesNotExist('Could not find a manager of type \
                .cart_manager.cart_total() from which to get the cart total')
        else:
            self.errors.append('There was no cart ID')
            return False

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
                try:
                    charge = stripe.Charge.create(**params)
                except stripe.error.CardError as e:
                    # Error if card was
                    # declined -; mainly
                    errors = {
                        'status':  e.http_status,
                        'type': e.error.type,
                        'code': e.error.code,
                        'param': e.error.param,
                        'message': e.error.message
                    }
                    self.errors.append(errors)
                    return False
                except stripe.error.RateLimitError as e:
                    self.errors.append('Rate limit exceeded')
                    return False
                except stripe.error.InvalidRequestError as e:
                    self.errors.append('Invalid request')
                    return False
                except stripe.error.AuthenticationError as e:
                    self.errors.append('Authentication error')
                    return False
                except stripe.error.APIConnectionError as e:
                    self.errors.append('API connection error')
                    return False
                except stripe.error.StripeError as e:
                    self.errors.append('Stripe error')
                    return False
                except Exception as e:
                    self.errors.append('Unknown error')
                    return False
            else:
                # A simple dict that passes the payment
                # as successful in order order to debug
                # the rest of the payment process
                charge = {'status': 'succeeded', 'id': 'FAKE ID'}

            if charge['status'] == 'succeeded':
                parameters = urlencode(
                    {
                        'reference': self.order_reference,
                        'transaction': charge['id']
                    }
                )
                # If the payment was successful,
                # then we can redirect the user
                # to the success page
                self.final_url = f'{self.cart_success}?{parameters}'

                if not payment_debug_mode:
                    self.request.session.pop('cart_id')
            else:
                self.errors.append('The charge has failed')
                return False
        else:
            self.errors.append('There was no total to charge to Stripe')
            return False

        return dict(status=True, reference=self.order_reference, \
            transaction=charge['id'], total=total_of_products_to_buy['cart_total'], redirect_url=self.final_url)

    @staticmethod
    def price_to_stripe(price):
        """A defintion that converts a decimal into a
        Stripe formatted number

        Example
        -------
            
            12.95€ should be 1295 for Stripe
        """
        if isinstance(price, dict):
            try:
                price = price['cart_total']
            except:
                raise KeyError('Could not get cart total from dict')
        return int(price) * 100

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
