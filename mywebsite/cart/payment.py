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
from django.shortcuts import reverse
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext_lazy as _

try:
    import stripe
except:
    raise ImportError(
        "You should install Stripe in order to use the payment logic."
    )
else:
    try:
        KEYS = settings.STRIPE_API_KEYS
    except:
        raise exceptions.ImproperlyConfigured(
            ("You should provide live and secret keys in STRIPE_API_KEYS to use the payment logic")
        )


def initialize_stripe():
    if settings.DEBUG:
        stripe.api_key = KEYS['test']['secret']
    else:
        stripe.api_key = KEYS['live']['secret']
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

stripe_is_valid = initialize_stripe()


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
        - kwargs: other values that you wish to integrate
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


class PaymentMixin:
    @staticmethod
    def price_to_stripe(price):
        """A defintion that converts a decimal into a
        Stripe formatted number

        Example
        -------
            
            12.95€ should be 1295 for Stripe
        """
        return int(float(price) * 100)

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
    def __init__(self, request, token_name='token'):
        self.stripe_token = request.POST.get(token_name)
        
        if not self.stripe_token:
            raise ValueError("You should provide a token from StripeJS")

        self.request = request
        # Create an order reference
        self.order_reference = create_payment_reference()

        self.total_of_products_to_buy = 0

        self.errors = []
        # The ID of the charge as returned
        # by the charge response
        self.charge_id = None
        # Create an internal transaction token for tracking
        # purposes for example
        self.transaction_token = create_transaction_token()

        self.cart_id = request.session.get('cart_id')

        self.new_or_existing_customer_id = None
        # These are errors to be shown in the
        # the front end of the website
        self.context_errors = []

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
        final_dictionnary = dict(
            order_reference=self.order_reference
        )

        try:
            cart_model = apps.get_model(settings.CART_MODEL)
        except:
            cart_model = apps.get_model('cart.Cart')

        if cart_model is None:
            raise exceptions.ImproperlyConfigured(('You should provide a model from which '
            'we can extract the cart total.'))
        
        try:
            self.cart_queryset = cart_model.objects.filter(cart_id__iexact=self.cart_id)
            # The model tries to get a cart_total() on the model
            # from a cart_manager() manager. It should return the total
            # sum of items that should be charged to Stripe
            total_of_products_to_buy = cart_model.cart_manager.cart_total(self.cart_id, as_value=True)



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
                self.total_of_products_to_buy = total_of_products_to_buy
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
                    errors = {
                        'status':  e.http_status,
                        'type': e.error.type,
                        'code': e.error.code,
                        'param': e.error.param,
                        'message': e.error.message
                    }
                    for error in errors:
                        self._build_new_display_error(error['message'])
                except stripe.error.RateLimitError as e:
                    self.errors.append('Rate limit exceeded')
                except stripe.error.InvalidRequestError as e:
                    self._build_new_display_error(f'INVALID REQUEST :: {e}')
                except stripe.error.AuthenticationError as e:
                    self.errors.append('Authentication error')
                except stripe.error.APIConnectionError as e:
                    self.errors.append('API connection error')
                except stripe.error.StripeError as e:
                    self._build_new_display_error(f'STRIPE ERROR :: {e}')
                except Exception as e:
                    self._build_new_display_error(f'OTHER :: {e}')
            else:
                # A simple dict that passes the payment
                # as successful in order order to debug
                # the rest of the payment process
                charge = {'status': 'succeeded', 'id': 'FAKE ID'}

        if charge:
            if charge['status'] == 'succeeded':
                self.charge_id = charge['id']
                url_parameters = {
                    'order_reference': self.order_reference,
                    'transaction': charge['id'],
                    'transaction_token': self.transaction_token
                }

                if payment_debug:
                    url_parameters['debug'] = True

                parameters = urlencode(url_parameters)

                self.final_url = f'{self.get_success_url()}?{parameters}'
                self.cart_queryset.update(paid_for=True)

                final_dictionnary.update({
                    'transaction': charge['id'],
                    'total': total_of_products_to_buy,
                    'redirect_url': self.final_url
                })
            else:
                self.errors.append('The charge was not successful')
                final_dictionnary.update({
                    'redirect_url': self.get_failed_url(),
                    'errors': self.errors,
                    'context_errors': self.context_errors
                })
        else:
            self.errors.append('There is no charge or charge not created')
            final_dictionnary.update({
                'redirect_url': self.get_failed_url(),
                'errors': self.errors,
                'context_errors': self.context_errors
            })

        if not self.errors:
            return (True, final_dictionnary)
        return (False, final_dictionnary)

    def _build_customer_creation_dict(self):
        customer_name = self._get_full_name(
            self.user_infos.get('firstname'), 
            self.user_infos.get('lastname')
        )
        address = {
            'line1': self.user_infos.get('address'),
            'city': self.user_infos.get('city'),
            'postal_code': self.user_infos.get('zip_code')
        }
        customer = {
            'source': self.stripe_token,
            'name': customer_name,
            'email': self.user_infos.get('email'),
            'phone': self.user_infos.get('telephone'),
            'address': {
                **address
            },
            'shipping': {
                'name': customer_name,
                'phone': self.user_infos.get('telephone'),
                'address': {
                    **address
                }
            }
        }
        return customer

    def _stripe_create_customer(self, data:dict):
        try:
            customer = stripe.Customer.create(**data)
        except (stripe.error.StripeError, Exception) as e:
            errors = {
                'status': e.http_status,
                'type': e.error.type,
                'code': e.error.code,
                'param': e.error.param,
                'message': e.error.message
            }
            for error in errors:
                self._build_new_display_error(error['message'])
            return False
        return customer['id']

    def _stripe_modify_customer(self, customer_id, data:dict):
        if customer_id is None:
            self._build_new_display_error('MODIFY CUSTOMER :: Customer ID is missing')
            return False
        try:
            customer = stripe.Customer.modify(customer_id, **data)
        except (stripe.error.StripeError, Exception) as e:
            self._build_new_display_error(f'MODIFY CUSTOMER :: {e}')
            return False
        return customer_id

    def create_stripe_customer_and_process_payment(self, payment_debug=False):
        """Creates a new Stripe customer and then proceeds
        to processing the payment
        """
        final_dictionnary = {
            'reference': self.order_reference,
            'redirect_url': self.get_failed_url(),
        }
        user_model = get_user_model()
        existing_customer = user_model.objects.filter(email=self.user_infos['email'])

        customer_creation_dict = self._build_customer_creation_dict()
        if not existing_customer.exists():
            state_or_id = self._stripe_create_customer(customer_creation_dict)
            if state_or_id:
                self.new_or_existing_customer_id = state_or_id
            else:
                final_dictionnary.update({
                    'errors': self.errors
                })
        else:
            item = existing_customer.get()
            profile = item.myuserprofile
            state_or_id = self._stripe_modify_customer(profile.stripe_customer_id, customer_creation_dict)
            if not state_or_id:
                final_dictionnary.update({
                    'errors': self.errors
                })
            else:
                self.new_or_existing_customer_id = state_or_id
        return self.process_payment(self.new_or_existing_customer_id, payment_debug=payment_debug)

    def set_session_for_post_process(self, **kwargs):
        """Often times, on the success page, you might have a script
        tag for Google Ads conversion. This helper definition sets the
        data for that tag directly in the session.
        """
        conversion = {
            'conversion': {
                'reference': self.order_reference,
                'transaction': self.charge_id or self.transaction_token
            }
        }
        kwargs.update(conversion)
        self.request.session.update(kwargs)
        return kwargs

    def create_new_order(self, payment_field=None, other_fields:dict={}):
        """
        A custom definition that updates a list of 
        models once the customer order was completed. 

        Parameters
        -----------

            - other_fields: a set other fields to update with their values
        """
        model = None
        try:
            model = apps.get_model(settings.CUSTOMER_ORDERS_MODEL)
        except:
            model = apps.get_model('cart.CustomerOrder')
        
        if model is not None:
            if not payment_field:
                payment_field = 'payment'

            if not hasattr(model, payment_field):
                raise AttributeError('Your model should provide a total or payment field in which we can write the total payment for the order')
            
            try:
                data = {
                    'user': self.request.user,
                    payment_field: self.total_of_products_to_buy,
                    'reference': self.order_reference,
                    'transaction': self.transaction_token,
                    **other_fields
                }
                new_order = model.objects.create(**data)
            except Exception as e:
                self.errors.append(f'Could not create order - {e}')
            else:
                return new_order
        else:
            self.errors.append('Could not find the Customer Order model')
        return False

    def create_new_customer_locally(self, **fields):
        """
        Convienience defintion for creating a new
        user/customer in the database
        """
        user_model = get_user_model()
        if not fields:
            use = ['email']
            for key, value in self.user_infos.items():
                if key in use:
                    fields.update({key: value})
        try:
            result = user_model.objects.get_or_create(**fields)
        except Exception as e:
            self._build_new_display_error(f'CREATE CUSTOMER :: {e}')
        else:
            return result

    def get_success_url(self):
        return reverse('cart:success')

    def get_failed_url(self):
        return reverse('cart:payment')

    def _build_new_display_error(self, message):
        base = f"""
        <div class="alert alert-danger mb-1">
            {message}
        </div>
        """
        new_alert = format_html(base, message=message)
        self.errors.append(message)
        self.context_errors.append(mark_safe(base))


class ApplePlay(SessionPaymentBackend):
    def process_payment(self):
        intent = stripe.PaymentIntent.create(
            amount=self.total_of_products_to_buy,
            currency='eur',
            # Verify your integration in this guide by including this parameter
            metadata={'integration_check': 'accept_a_payment'},
        )
        return intent
