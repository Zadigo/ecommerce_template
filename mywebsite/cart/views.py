import json
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET, require_POST
from django.views.generic.list import (BaseListView,
                                       MultipleObjectTemplateResponseMixin)

from cart import emailing, forms, models, payment, utilities
from cart.tasks import purchase_complete_email


class BaseCartView(MultipleObjectTemplateResponseMixin, BaseListView):
    """
    This is the base class for implement functonnalities to views
    that require functionnalities for e-commerce payments
    """
    model = models.Cart
    cart_filters = {}
    no_cart_url = None
    session_cart_name = 'cart_id'
    context_object_name = 'cart_products'

    def dispatch(self, request, *args, **kwargs):
        if not self.no_cart_url:
            redirect_url = reverse('cart:no_cart')
        else:
            redirect_url = self.no_cart_url
        if not self.get_queryset().exists():
            return HttpResponseRedirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get_cart_id(self):
        return self.request.session.get(self.session_cart_name)

    def get_queryset(self):
        cart_id = self.get_cart_id()
        cart = self.model.cart_manager.cart_products(cart_id)
        return cart

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        cart_id = self.get_cart_id()
        total = self.model.cart_manager.cart_total(cart_id, as_value=True)
        context = {
            'object_list': queryset,
            'cart_id': cart_id,
            'cart_total': total
        }
        context_object_name = super().get_context_object_name(queryset)
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        return super().get_context_data(**context)


class CheckoutView(BaseCartView):
    template_name = 'pages/cart.html'


@method_decorator(cache_control(private=True), name='dispatch')
class ShipmentView(BaseCartView):
    template_name = 'pages/shipment.html'


@method_decorator(never_cache, name='dispatch')
class PaymentView(BaseCartView):
    template_name = 'pages/payment.html'

    def post(self, request, **kwargs):
        payment.PreprocessPayment(request, set_in_session=True, shipping='standard')
        return render(request, self.template_name, super().get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tax'] = 20
        context['shipping'] = 2.99
        context['uuid'] = uuid4()
        return context


class ProcessPaymentView(generic.View):
    send_email = False
    user_fields = ['firstname', 'lastname']
    profile_fields = ['telephone', 'address', 'city', 'zip_code']

    @transaction.atomic
    def post(self, request, **kwargs):
        backend = payment.SessionPaymentBackend(request)

        confirmation_email = emailing.OrderConfirmationEmail()
        failed_email = emailing.FailedOrderEmail()

        try:
            payment_is_in_debug_mode = settings.STRIPE_DEBUG
        except:
            payment_is_in_debug_mode = True

        state, data = backend.create_stripe_customer_and_process_payment(
            payment_debug=payment_is_in_debug_mode
        )
        return_data = {
            'state': state, 
            **data
        }

        if state:
            # Even though the order fails to be created in
            # our database, bring the customer to 
            # the success page anyways since the payment 
            # has been successful with Stripe
            order = backend.create_new_order()
            if order:
                order.cart.add(*list(backend.cart_queryset))

                backend.set_session_for_post_process()

                user, created = backend.create_new_customer_locally()
                # When the customer has been created or retrieved,
                # we'll update their informations with what they
                # have provided us in the shipment form
                for field in self.user_fields:
                    setattr(user, field, backend.user_infos.get(field, None))
                user.save()
                sid = transaction.savepoint()                
                
                profile = user.myuserprofile
                for field in self.profile_fields:
                    setattr(profile, field, backend.user_infos.get(field, None))
                if created:
                    profile.stripe_customer_id = backend.new_or_existing_customer_id
                profile.save()
                transaction.savepoint_commit(sid)

                order.user = user
                order.save()
            else:
                pass
        return JsonResponse(data=return_data)


@method_decorator(cache_control(private=True), name='dispatch')
class CartSuccessView(BaseCartView):
    template_name = 'pages/success.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        request.session.pop('cart_id')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversion = self.request.session.get('conversions')
        if conversion is not None:
            context['transaction'] = conversion['transaction']
            context['order_reference'] = conversion['order_reference']
        return context


class EmptyCartView(generic.TemplateView):
    template_name = 'pages/no_cart.html'


@require_POST
def add_to_cart(request, **kwargs):
    state = False
    data = json.loads(request.body)
    model = utilities.get_product_model()
    product = model.objects.get(data['id'])

    cart = models.Cart.cart_manager.add_to_cart(request, product)
    return_data = {'state': state}
    if cart:
        return_data['state'] = True
    return JsonResponse(data=return_data)


@require_POST
def apply_coupon(request, **kwargs):
    coupon = request.POST.get('coupon')

    form = forms.CouponForm(request.POST)

    if form.is_valid():
        try:
            coupon = models.Discount.objects.get(code=coupon)
        except:
            return redirect('shipment')
        else:
            # cart_id = request.session.get('cart_id')
            # cart = models.Cart.objects.filter(cart_id=cart_id)
            # cart.update(coupon=coupon)
            return redirect('shipment')
    else:
        return redirect('shipment')


@require_GET
@transaction.atomic
def delete_product_from_cart(request, **kwargs):
    cart_id = request.session.get('cart_id')
    base_message = {
        'request': request,
        'extra_tags': 'alert-danger'
    }
    if cart_id:
        products = models.Cart.objects.filter(cart_id__iexact=cart_id)
        items = products.filter(pk=kwargs['pk'])
        if items.exists():
            item = items.get()

            item.delete()
            # Refesh the queryset and get the
            # actual count of items
            items_count = items.all().count()

            if items_count == 0 or not items_count:
                return redirect(reverse('cart:no_cart'))

            if items_count >= 1:
                return redirect(reverse('cart:checkout'))

        else:
            base_message['message'] = _("Une erreur s'est produite - CHE-NF")
            messages.error(**base_message)

    return redirect(reverse('cart:no_cart'))


@require_GET
def alter_item_quantity(request, **kwargs):
    accepted_methods = ['add', 'reduce']
    method = kwargs.get('method')
    if method not in accepted_methods:
        messages.error(request, _("Quelque chose c'est mal passé - CX-ATOC"), extra_tags='alert-danger')
        return redirect(reverse('cart:shipment'))

    cart_id = request.session.get('cart_id')
    if cart_id:
        user_carts = models.Cart.objects.filter(cart_id=cart_id)
        try:
            cart_to_alter = user_carts.get(id=kwargs['pk'])
        except:
            messages.error(request, _("Le panier n'existe pas"), extra_tags='alert-danger')
            return redirect(reverse('cart:checkout'))
        else:
            quantity = cart_to_alter.quantity
            if method == 'add':
                quantity = quantity + 1
            elif method == 'reduce':
                quantity = quantity - 1

                # If the user only had one
                # thing in his cart, by deleting
                # that single thing we know that
                # there is nothing left
                if quantity < 1 and user_carts.count() == 1:
                    cart_to_alter.delete()
                    return redirect(reverse('cart:no_cart'))

            cart_to_alter.quantity = quantity
            cart_to_alter.save()

        return redirect(reverse('cart:checkout'))
    else:
        messages.error(
            request, _("Ce panier n'existe pas"), extra_tags='alert-warning')
    return redirect(reverse('cart:checkout'))
