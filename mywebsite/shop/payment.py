import ast
import datetime
import hashlib
import json
import os
import secrets
from urllib.parse import urlencode

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import exceptions
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.http import QueryDict
from django.utils.translation import gettext_lazy as _

try:
    import stripe
except:
    raise ImportError(_("You should install Stripe in order to use the payment logic."))
else:
    try:
        KEYS = settings.STRIPE_API_KEYS
    except:
        raise exceptions.ImproperlyConfigured(_("You should provide live and secret keys in STRIPE_API_KEYS to use the payment logic"))


def initialize_stripe():
    if settings.DEBUG:
        stripe.api_key = KEYS['test']['secret']
    else:
        stripe.api_key = KEYS['live']['secret']
        # stripe.ApplePayDomain.create(domain_name=settings.APPLE_PAY_DOMAIN)
    return True


def stripe_context_processor(request):
    """Return the publisheable key directly in the context
    of the application
    """
    context = dict()
    if settings.DEBUG:
        context.update({'publishable_key': KEYS['test']['publishable']})
    else:
        context.update({'publishable_key': KEYS['live']['publishable']})
    return context

is_valid = initialize_stripe()


def create_payment_reference(n=5):
    """Create a basic reference: `NAW201906126011b0e0b8`
    """
    current_date = datetime.datetime.now().date()
    prefix = f'NAW{current_date.year}{current_date.month}{current_date.day}'
    return prefix + secrets.token_hex(n)


def create_transaction_token(n=1, salt='mywebsite'):
    """Create a payment token for Google enhanced ecommerce"""
    tokens = [secrets.token_hex(2) for _ in range(0, n)]
    # Append the salt that allows us to identify
    # if the payment method is a valid one
    tokens.append(hashlib.sha256(salt.encode('utf-8')).hexdigest())
    return '-'.join(tokens)


class PreprocessPayment:
    """A helper class used just before the user accesses the
    payment page. It gathers and checks all the important informations
    such as the firstname, the lastname or address and then
    returns them or sets them in the session.

    Parameters
    ----------

        - request: the http request
        - set_in_session: set the gathered values in the session
    """
    def __init__(self, request, set_in_session=False, **kwargs):
        internal_dict = dict()
        # We receive a QueryDict here. Transform
        # it to a regular dict and copy
        if isinstance(request, WSGIRequest):
            data = request.POST.dict().copy()
            data.pop('csrfmiddlewaretoken')

            for key, value in data.items():
                if key != 'csrfmiddlewaretoken':
                    internal_dict.update({key: value})

            self.user_infos = {**self._check_final_dict(internal_dict), **kwargs}
            self.fitted_user_infos = self._fit_dictionnary(self.user_infos)

            if set_in_session:
                request.session.update({'user_infos': self.fitted_user_infos})
        else:
            raise ValueError("'request' should be an instance of WSGIRequest got: %s" % request)

    def _fit_dictionnary(self, data):
        """Normalizes the Python dictionnary for Javascript or other
        template requirements"""
        items = str(self.user_infos).replace("\'", "\"")
        return f'{json.loads(items)}'

    @staticmethod
    def _check_final_dict(values:dict):
        """Checks that the incomming dictionnary has all the required
        fields in order to create the payment in stripe
        """
        key_errors = []

        incoming_keys = values.keys()
        required_keys = ['firstname', 'lastname', 'email', 'telephone', 
            'address', 'country', 'city', 'zip_code']

        for key in incoming_keys:
            if key not in required_keys:
                key_errors.append(key)

        if key_errors:
            raise ValueError(f"In order to create a payment, you need to ' \
                'provide these required keys: {', '.join(key_errors)}")

        return values


class PostProcessPayment:
    """Call this class once the payment process has been
    completed. It cleans the sessions from the `user infos`
    and adds a `transaction token` that can be used later on.
    """
    def __init__(self, request, enforce_comparision=False, 
                 token_name=None, *models_to_update):
        self.is_authorized = False

        order_reference = request.session.get('conversion')['reference']

        if enforce_comparision:
            result = self.compare(
                request.GET.get('transaction_token'),
                request.session.get('transaction_token')
            )
            if result:
                self.is_authorized = True

        if order_reference:
            self.is_authorized = True

    @staticmethod
    def compare(url_token, session_token):
        """Use this definition to check if a url token
        is equals to a session based token. This can be
        helpful for authorizing a user on a specific page
        in the cart e.g. success page.
        """
        return url_token == session_token
            
class PaymentMixin:
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
                raise KeyError('Could not get "cart_total" from dict')
        return int(price) * 100

    @staticmethod
    def _get_full_name(name, surname):
        return f'{name} {surname}'

    @staticmethod
    def extract_from_string(user_infos:str):
        """If it happens that the dictionnary from the session
        is a string object, this defintion extracts it"""
        return ast.literal_eval(user_infos)

class SessionPaymentBackend(PaymentMixin):
    """
    This class is the main entrypoint for creating a session
    based payment with Stripe.

    Description
    -----------

        The flow of a stripe payment is the following:
            1. Stripe JS
            2. SessionBasedBacked
            3. Stripe JS

    Parameters
    ----------

        token_name: the stripe token to retrieve based on the name provided in the POST request
        from your payment page e.g. {token: tok_ABC}

    Result
    ------

        Returns a tuple of values such as:
            (   state,
                {
                    order_reference: ABC,
                    transaction: ch_ABC,
                    total: 0.00,
                    redirect_url: /
                }
            )

        NOTE: The transaction is the one created and returned by Stripe in the payment response
        when the payment is completed.

        Finally, the state is either True or False. The way the payment state becomes True is if
        the process was completed without any errors appended in the error array.
    """
    cart_model = None
    success_url = '/shop/cart/success'
    fail_url = '/shop/cart/payment'

    def __init__(self, request, token_name='token'):
        initialize_stripe()
        self.stripe_token = request.POST.get(token_name)
        
        if not self.stripe_token:
            raise ValueError("You should provide a token from StripeJS")

        self.request = request
        # Create an order reference
        self.order_reference = create_payment_reference()

        self.total_of_products_to_buy = 0
        # This parameter returns a charge
        # object that can be used for other
        # kinds of processing afterwards
        self.completed_charge = dict()
        # Access the user once the payment
        # process has been done
        self.anonymous_user = self.request.is_anonymous

        self.errors = []

        # The ID of the charge as returned
        # by the charge response
        self.charge_id = None
        # Create an internal transaction token for tracking
        # purposes for example
        self.transaction_token = create_transaction_token()

        self.cart_id = request.session.get('cart_id')

        if not self.cart_id:
            raise ValueError(_("You should provide a cart ID number to identify the user's cart"))

        user_infos = request.session.get('user_infos')

        if not user_infos:
            raise ValueError(_("In order to create a payment, you need to provide user informations such as firstname, lastname..."))
        else:
            if isinstance(user_infos, str):
                self.user_infos = self.extract_from_string(user_infos)
            elif isinstance(user_infos, dict):
                self.user_infos = user_infos

    def process_payment(self, customer_id=None, payment_debug=False, **kwargs):
        """
        Main definition for processing a payment with Stripe

        Parameters
        ----------

            - customer_id: a Stripe customer id
            - payment_debug: run this process in debug mode [i.e. without factually hitting the Stripe API]
        """
        final_dictionnary = dict()

        if self.cart_model is None:
            raise exceptions.ImproperlyConfigured(('You should provide a model from which '
            'we can extract the cart total.'))

        try:
            self.cart_queryset = self.cart_model.objects.filter(cart_id__iexact=self.cart_id)
            # The model tries to get a get_cart_total() on the model
            # from a cart_manager() model manager. It should return the total
            # sum of items that should be charged to Stripe
            total_of_products_to_buy = self.cart_model.cart_manager.cart_total(self.cart_id)



            # REWRITTEN:
            # custom_manager = getattr(cart_model, 'manager', None)
            # if not custom_manager:
            #     custom_manager = getattr(cart_model, 'get_cart_products', None)
            #     if not custom_manager:
            #         raise exceptions.ImproperlyConfigured("Your Cart model should provide a get_cart_product() a method from which the products which a part of a cart can be extracted")
            # else:
            #     self.cart_queryset = custom_manager.get_cart_products(self.cart_id)

            # custom_manager = getattr(cart_model, 'manager', None)
            # if not custom_manager:
            #     custom_method = getattr(cart_model, 'get_cart_total', None)
            #     if not custom_method:
            #         raise exceptions.ImproperlyConfigured("Your Cart model should provide a get_cart_total() or get_cart_total() method from which the products which we can extract the cart's total")

            # if custom_manager and not custom_method:
            #     total_of_products_to_buy = custom_manager.get_cart_total(self.cart_id)
            # else:
            #     total_of_products_to_buy = custom_method()

        except:
            raise exceptions.ObjectDoesNotExist(('Could not find a manager of type '
                '.cart_manager.cart_total() from which to get the cart total'))
        else:
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
                    'description': f'Order for cart {self.cart_id}',
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
                        'name': self._get_full_name(self.user_infos['firstname'], self.user_infos['lastname']),
                        'order_reference': self.order_reference,
                        'shipping': self.user_infos['shipping']
                    }
                }

                if 'tracking_number' in kwargs and 'carrier' in kwargs:
                    params.update(
                        {
                            'tracking_number': kwargs['shipping']['tracking_number'],
                            'carrier': kwargs['shipping']['carrier']
                        }
                    )

                if customer_id:
                    # To create a customer and charge the card,
                    # we need to create the customer first and then
                    # charge that customer with his card
                    params.pop('source')
                    params.update({'customer': customer_id})
            else:
                self.errors.append('There was no total to charge to Stripe')

            charge = None
            if not payment_debug:
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
                except stripe.error.RateLimitError as e:
                    self.errors.append('Rate limit exceeded')
                except stripe.error.InvalidRequestError as e:
                    self.errors.append('Invalid request')
                except stripe.error.AuthenticationError as e:
                    self.errors.append('Authentication error')
                except stripe.error.APIConnectionError as e:
                    self.errors.append('API connection error')
                except stripe.error.StripeError as e:
                    self.errors.append('Stripe error')
                except Exception as e:
                    self.errors.append('Unknown error')
            else:
                # A simple dict that passes the payment
                # as successful in order order to debug
                # the rest of the payment process
                charge = {'status': 'succeeded', 'id': 'FAKE ID'}

        if charge:
            if charge['status'] == 'succeeded':
                self.charge_id = charge['id']
                parameters = urlencode(
                    {
                        'order_reference': self.order_reference,
                        'transaction': charge['id'],
                        'transaction_token': self.transaction_token
                    }
                )

                # If the payment was successful,
                # then we can redirect the user
                # to the success page
                self.final_url = f'{self.success_url}?{parameters}'

                final_dictionnary.update({
                    'order_reference': self.order_reference,
                    'transaction': charge['id'],
                    'total': total_of_products_to_buy['cart_total'],
                    'redirect_url': self.final_url
                })
            else:
                final_dictionnary.update({
                    'reference': self.order_reference,
                    'redirect_url': self.fail_url,
                    'errors': self.errors
                })
                self.errors.append('The charge was not successful')
        else:
            final_dictionnary.update({
                'reference': self.order_reference,
                'redirect_url': self.fail_url,
                'errors': self.errors
            })
            self.errors.append('There is no charge')

        if not self.errors:
            if not payment_debug:
                self.request.session.pop('cart_id')
            return (True, final_dictionnary)

        return (False, final_dictionnary)

    def create_customer_and_process_payment(self, payment_debug=False):
        # TODO: Make final dict a global element
        final_dictionnary = {}
        customer_name = self._get_full_name(self.user_infos['firstname'], self.user_infos['lastname'])
        customer = {
            'source': self.stripe_token,
            'name': customer_name,
            'email': self.user_infos['email'],
            'phone': '',
            'address': {
                'line1': self.user_infos['address'],
                'city': self.user_infos['city'],
                'postal_code': self.user_infos['zip_code']
            },
            'shipping': {
                'name': customer_name,
                'phone': '',
                'address': {
                    'line1': self.user_infos['address'],
                    'city': self.user_infos['city'],
                    'postal_code': self.user_infos['zip_code']
                }
            }
        }

        try:
            customer = stripe.Customer.create(**customer)
        except (stripe.error.StripeError, Exception) as e:
            errors = {
                'status':  e.http_status,
                'type': e.error.type,
                'code': e.error.code,
                'param': e.error.param,
                'message': e.error.message
            }
            self.errors.append(errors)
            final_dictionnary.update({
                'reference': self.order_reference,
                'redirect_url': self.fail_url,
                'errors': self.errors
            })
        else:
            return self.process_payment(customer['id'], payment_debug=payment_debug)

    def set_session_for_post_process(self, **kwargs):
        """Often times, on the success page, you might have a script
        tag for Google Ads conversion. This helper definition sets the
        data for that tag directly in the session.
        """
        conversion = {
            'conversion': {
                'reference': self.order_reference,
                'transaction': self.charge_id or self.transaction_token,
                'payment': str(self.total_of_products_to_buy)
            }
        }
        # conversion['conversion'] = {**conversion['conversion'], **kwargs}
        self.request.session.update(conversion)
        return conversion

    def update_models(self, order_model_name=None, 
                      payment_field=None, other_fields:dict = None,
                      create_user=False, model=None):
        """
        A custom definition that updates a list of 
        models once the customer order was completed. 

        Parameters
        -----------

            - other_fields: a set other fields to update with their values
        """
        customer_order_model = None
        if model:
            if model.__name__ == 'CustomerOrder' \
                    or model.__name__ == order_model_name:
                customer_order_model = model
        else:
            models = apps.get_models()
            for model in models:
                name = getattr(model, '__name__')
                if name == 'CustomerOrder':
                    model = model
                    break
            
            if not model:
                raise exceptions.ImproperlyConfigured(_("You should provide a valid Orders model if you wish to update your model after purchase"))

        if not payment_field:
            payment_field = 'product'
        
        if not hasattr(customer_order_model, payment_field):
            raise AttributeError(_("Your model should have a total or payment field to which we can write the total payment for the the order"))

        new_order = customer_order_model.objects.create(
            **{'user': self.request.user, payment_field: self.total_of_products_to_buy, **other_fields}
        )
        return new_order

    def create_user(self, **fields):
        """
        Coonvienience defintion for creating a new
        user in the your database
        """
        user_model = get_user_model()
        user_model.objects.create(**fields)


class ApplePlay(SessionPaymentBackend):
    def process_payment(self):
        intent = stripe.PaymentIntent.create(
            amount=self.total_of_products_to_buy,
            currency='eur',
            # Verify your integration in this guide by including this parameter
            metadata={'integration_check': 'accept_a_payment'},
        )
        return intent
