"""

    Conversion Tunnel
    ------

        checkout > shipment > payment > success

    Payment process
    -------

        1. On submitting the form, an AJAX request is
           done using Stripe in order to get the token

        2. An intermediate view is used afterwards to
           process the payment ofn the backend side

        3. If the payment was successful, a redirect is
           done to the SuccessView
"""

import random
from ast import literal_eval

from django import http, shortcuts
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import cache, exceptions, paginator
from django.core import serializers as core_serializers
from django.core.cache import caches
from django.db import transaction as atomic_transactions
from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators import http as http_decorator
from django.views.decorators import vary
from django.views.decorators.cache import (cache_control, cache_page,
                                           never_cache)
from django.views.decorators.csrf import csrf_exempt

from accounts import models as accounts_models
from shop import (emailing, forms, models, payment, serializers, tasks,
                  utilities)


def create_products_impressions(queryset):
    """Create impressions for Google Analytics"""
    impressions = []
    if queryset is None:
        return []
    for index, product in enumerate(queryset):
        impressions.append(dict(id=product.reference, \
                name=product.name, price=product.get_price(), brand='Nawoka', \
                    category=product.collection.name, position=index, \
                        list=f'{product.collection.gender}/{product.collection.name}'))
    return impressions

def create_cart_impressions(constructed_products):
    impressions = []
    if isinstance(constructed_products, dict):
        constructed_products = constructed_products['constructed_products']

    for index, product in enumerate(constructed_products):
        item = {
            'cart_id': product['cart_id'], 
            'brand': 'Nawoka', 
            'position': index, 
            'price': product['price_ht']
        }
        impressions.append(item)
    return impressions

def creat_cart_products_from_queryset(queryset):
    impressions = []
    for cart in queryset:
        item = {
                'id': cart.product.reference,
                'name': cart.product.name,
                'brand': 'Nawoka',
                'category': cart.product.collection.name,
                'price': cart.product.get_price(),
                'quantity': cart.quantity
            }
        impressions.append(item)
    return impressions


@method_decorator(cache_page(60 * 30), name='dispatch')
class IndexView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'pages/shop.html')


class LookBookView(generic.TemplateView):
    template_name = 'pages/lookbook.html'


class ShopGenderView(generic.View):
    def get(self, request, *args, **kwargs):
        collections = models.ProductCollection.objects.filter(gender=kwargs['gender'])
        context = {
            'collections': collections[:3]
        }
        return render(request, 'pages/shop_gender.html', context)


class ProductsView(generic.ListView):
    model = models.ProductCollection
    template_name = 'pages/collections.html'
    context_object_name = 'products'
    paginate_by = 12
    ordering = '-created_on'

    def get_queryset(self, **kwargs):
        collection_name = self.kwargs['collection']
        gender = self.kwargs['gender']

        try:
            collection = models.ProductCollection.objects.get(view_name__exact=collection_name, gender=gender)
        except:
            raise http.Http404("La collection n'existe pas")
        else:
            queryset = collection.product_set.filter(active=True, private=False)
            
            authorized_categories = ['all', 'promos', 'favorites']
            category = self.request.GET.get('category')

            if not category or category == '':
                return queryset

            if category in authorized_categories:
                if category == 'all':
                    return queryset
                elif category == 'promos':
                    return queryset.filter(discounted=True)
                elif category == 'favorites':
                    return queryset.filter(our_favorite=True)
            else:
                return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_queryset(**kwargs)

        # Set a specific pagination number to
        # active depending on which page we are
        # current_active_page = self.request.GET.get('page')
        # if not current_active_page:
        #     current_active_page = 1
        # context['current_active_page'] = current_active_page

        # klass = super().get_paginator(products, self.paginate_by)
        
        # serialized_products = serializers.ProductSerializer(instance=klass.object_list, many=True)
        # context['vue_products'] = serialized_products.data

        collection = self.model.objects.get(view_name__exact=self.kwargs['collection'], gender=self.kwargs['gender'])
        context['collection'] = collection

        context['impressions'] = create_products_impressions(products)
        return context


@method_decorator(cache_page(60 * 15), name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ProductView(generic.DetailView):
    model = models.Product
    queryset = models.Product.objects.all()
    template_name = 'pages/product.html'
    context_object_name = 'product'

    def post(self, request, **kwargs):
        product = super().get_object()
        # TODO: Add a method function that prevent
        # triggering the rest of the method with 
        # any kinds of post requests
        cart = models.Cart.cart_manager.add_to_cart(request, product)
        if cart:
            return http.JsonResponse(data={'success': 'success'})
        else:
            return http.JsonResponse(data={'failed': 'missing parameters'}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = super().get_object()

        serialized_product = serializers.ProductSerializer(instance=product)
        context['vue_product'] = serialized_product.data

        suggested_products = self.model.objects.prefetch_related('images') \
                                    .filter(active=True).exclude(id=product.id)[:3]
        context['more'] = suggested_products
        context['impressions'] = create_products_impressions(suggested_products)

        return context


class PreviewProductView(LoginRequiredMixin, generic.DetailView):
    """
    This is a custom view for previewing on a product
    in the semi-original context of the main product page
    """
    model = models.Product
    queryset = models.Product.objects.all()
    template_name = 'pages/preview.html'
    context_object_name = 'product'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        content = super().get(request, *args, **kwargs)
        if not request.user.is_admin:
            return http.HttpResponseForbidden('You are not authorized on this page')
        return content

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = super().get_object()

        serialized_product = serializers.ProductSerializer(instance=product)
        context['vue_product'] = serialized_product.data
        
        return context


@method_decorator(cache_page(60 * 30), name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class PrivateProductView(generic.DetailView):
    """
    This is a special custom view for creating products in a non
    classified manner and one that does not appear in the in the
    urls of the main site --; this can be perfect for testing
    a product from a marketing perspective.
    """
    model = models.Product
    queryset = models.Product.product_manager.private_products()
    template_name = 'pages/product.html'
    context_object_name = 'product'

    def post(self, request, **kwargs):
        product = super().get_object()
        # TODO: Add a method function that prevent
        # triggering the rest of the method with 
        # any kinds of post requests
        cart = models.Cart.cart_manager.add_to_cart(request, product)
        if cart:
            return http.JsonResponse(data={'success': 'success'})
        else:
            return http.JsonResponse(data={'failed': 'missing parameters'}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = super().get_object()

        serialized_product = serializers.ProductSerializer(instance=product)
        context['vue_product'] = serialized_product.data
        
        return context    


class CheckoutView(generic.ListView):
    model = models.Cart
    template_name = 'pages/cart.html'
    context_object_name = 'constructed_products'

    def get(self, request, **kwargs):
        # TODO: Make sure when the customer
        # reduces the cart and it goes to
        # zero to delete the cart ID from
        # his session
        get_request = super().get(request)

        cart_id = self.request.session.get('cart_id')
        if cart_id is None:
            return redirect('no_cart')

        queryset = super().get_queryset().filter(cart_id=cart_id)
        if not queryset.exists():
            return redirect('no_cart')
        return get_request

    def post(self, request, **kwargs):
        return http.JsonResponse({'success': 'success'})
    
    def get_queryset(self, **kwargs):
        cart_id = self.request.session.get('cart_id')
        return models.Cart.cart_manager.cart_products(cart_id)

    def get_context_data(self, **kwargs):
        products = super().get_queryset()
        context = super().get_context_data()

        context['vue_products'] = self.get_queryset()

        products = self.get_queryset(**kwargs)['constructed_products']
        context['impressions'] = create_cart_impressions(products)

        cart_id = self.request.session.get('cart_id')
        context['cart_total'] = self.model.cart_manager.cart_total(cart_id)['cart_total']
        return context


@method_decorator(cache_control(private=True), name='dispatch')
class ShipmentView(generic.ListView):
    model = models.Cart
    template_name = 'pages/shipment.html'
    context_object_name = 'products'

    def get(self, request, **kwargs):
        get_request = super().get(request)

        cart_id = self.request.session.get('cart_id')
        if cart_id is None:
            return redirect('no_cart')
            
        queryset = super().get_queryset().filter(cart_id=cart_id)
        if not queryset.exists():
            return redirect('no_cart')
        return get_request

    def get_queryset(self, **kwargs):
        cart_id = self.request.session.get('cart_id')
        return models.Cart.cart_manager.cart_products(cart_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_queryset(**kwargs)
        cart_id = self.request.session.get('cart_id')

        context['cart_id'] = cart_id
        context['coupon_form'] = forms.CouponForm
        # context['has_coupon'] = self.get_queryset().first().coupon.has_coupon
        context['cart_total'] = self.model.cart_manager.cart_total(cart_id)['cart_total']

        context['impressions'] = create_cart_impressions(products)
        return context


@method_decorator(never_cache, name='dispatch')
class PaymentView(generic.ListView):
    model = models.Cart
    template_name = 'pages/payment.html'
    context_object_name = 'products'

    def get(self, request, **kwargs):
        get_request = super().get(request)

        cart_id = self.request.session.get('cart_id')
        if cart_id is None:
            return redirect(reverse('no_cart'))
            
        queryset = super().get_queryset().filter(cart_id=cart_id)
        if not queryset.exists():
            return redirect('no_cart')
        return get_request

    def post(self, request, **kwargs):
        context = self.get_context_data(object_list=self.get_queryset(), **kwargs)
        payment.PreprocessPayment(request, set_in_session=True, shipping='standard')
        return render(request, self.template_name, context)

    def get_queryset(self, **kwargs):
        cart_id = self.request.session.get('cart_id')
        return models.Cart.cart_manager.cart_products(cart_id)

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        products = self.get_queryset(**kwargs)
        cart_id = self.request.session.get('cart_id')
        context['cart_id'] = cart_id
        context['cart_total'] = self.model.cart_manager.cart_total(cart_id)['cart_total']
        context['impressions'] = create_cart_impressions(products)
        return context


class ProcessPayment(generic.View):
    def post(self, request, **kwargs):
        backend = payment.SessionPaymentBackend(request)
        backend.cart_model = models.Cart
        # state, data = backend.process_payment(payment_debug=False)
        state, data = backend.create_customer_and_process_payment()
        
        confirmation_email = emailing.OrderConfirmationEmail()
        
        if state:
            details = {
                'reference': data['order_reference'],
                'transaction': data['transaction'],
                'payment': data['total']
            }
            
            try:
                order = models.CustomerOrder.objects.create(**details)
                order.cart.add(*list(backend.cart_queryset))
            except:
                return http.JsonResponse(data={'state': state, 'redirect_url': '/shop/payment'})
            else:
                backend.set_session_for_post_process()

                user, _ = accounts_models.MyUser.objects.get_or_create(email=backend.user_infos['email'])

                user.name = backend.user_infos['firstname']
                user.surname = backend.user_infos['lastname']
                user.save()

                profile = user.myuserprofile_set.get()
                profile.telephone = backend.user_infos['telephone']
                profile.address = backend.user_infos['address']
                profile.city = backend.user_infos['city']
                profile.zip_code = backend.user_infos['zip_code']

                profile.save()

                order.user = user
                order.save()

                # confirmation_email.process(
                #     request, 'contact.mywebsite@gmail.com',
                #     user.email,
                #     '', 
                #     profile.get_full_address(), 
                #     order.reference, 1, 
                #     user.name,
                #     order_total=order.payment
                # )
        else:
            return http.JsonResponse(data={'state': state, 'redirect_url': data['redirect_url'], 'code': data['errors'][0]['code']})
        return http.JsonResponse(data={'state': state, 'redirect_url': data['redirect_url']})


@method_decorator(cache_control(private=True), name='dispatch')
class CartSuccessView(generic.TemplateView):
    template_name = 'pages/success.html'

    def get(self, request, *args, **kwargs):
        context = {}
        data = request.session.get('conversion')

        backend = payment.PostProcessPayment(request)

        if backend.is_authorized:
            customer_order = models.CustomerOrder.objects.get(reference=data['reference'])
            products = customer_order.cart.all()
            context['products'] = creat_cart_products_from_queryset(products)
            context['payment'] = data['payment']
            context['transaction'] = data['transaction']
            context['reference'] = data['reference']
            return render(request, 'pages/success.html', context=context)
        else:
            return redirect('no_cart')


class EmptyCartView(generic.TemplateView):
    template_name = 'pages/no_cart.html'


@http_decorator.require_POST
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


class SearchView(generic.ListView):
    model = models.Product
    template_name = 'pages/search.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self, **kwargs):
        searched_item  = self.request.GET.get('q')
        if searched_item is None:
            return []
        return self.model.product_manager.search_product(searched_item)

    def get_context_data(self, **kwargs):
        products = self.get_queryset(**kwargs)

        context = super().get_context_data(**kwargs)
        klass = super().get_paginator(self.get_queryset(**kwargs), self.paginate_by)

        serialized_products = serializers.ProductSerializer(instance=klass.object_list, many=True)
        context['vue_products'] = serialized_products.data

        # TODO
        collections = ['tops', 'pantalons']
        random_collection = random.choice(collections)
        collection = models.ProductCollection.objects.get(view_name=random_collection)
        proposed_products = collection.product_set.all()[:4]
        context['proposed_products'] = proposed_products

        context['impressions'] = create_products_impressions(products)
        return context
  
  
class SpecialOfferView(generic.DetailView):
    model = models.Discount
    template_name = 'pages/product.html'
    context_object_name = 'product'

    def get_queryset(self):
        offer = models.Discount.\
            objects.get(reference=self.kwargs['pk'])
        try:
            product = offer.product.get(reference=self.kwargs['product_reference'])
        except exceptions.ObjectDoesNotExist:
            return redirect('shop_gender', 'femme')
        else:
            return product
            

@http_decorator.require_GET
def delete_product_from_cart(request, **kwargs):
    cart_id = request.session.get('cart_id')
    if cart_id:
        products = models.Cart.objects.filter(cart_id__iexact=cart_id)
        if products.exists():
            try:
                product = products.get(pk=kwargs['pk'])
            except:
                messages.error(request, _("Une erreur s'est produite - CHE-DE"))
                return redirect('checkout')

            try:
                with atomic_transactions.atomic():
                    product.delete()
            except:
                messages.error(request, _("Une erreur s'est produite - CHE-DE"))
                return redirect('checkout')

            products_count = models.Cart.cart_manager.number_of_products(
                cart_id)

            # When the cart is completely empty,
            # this returns None which in return
            # throws a TypeError becaause None cannot
            # be compared to int
            if not products_count['quantity__sum']:
                return redirect('no_cart')

            if products_count['quantity__sum'] > 1:
                return redirect('checkout')

    return redirect('no_cart')


@http_decorator.require_GET
def alter_item_quantity(request, **kwargs):
    accepted_methods = ['add', 'reduce']
    if 'method' in kwargs:
        if kwargs['method'] not in accepted_methods:
            messages.error(
                request, _("Quelque chose c'est mal passé - CX-ATOC"), extra_tags='alert-danger')

    cart_id = request.session.get('cart_id')
    if cart_id:
        method = kwargs['method']
        user_carts = models.Cart.objects.filter(cart_id=cart_id)
        try:
            cart_to_alter = user_carts.get(id=kwargs['pk'])
        except:
            messages.error(request, _("Le panier n'existe pas"), extra_tags='alert-warning')
            return redirect('checkout')
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
                    return redirect('no_cart')

            cart_to_alter.quantity = quantity
            cart_to_alter.save()

        return redirect('checkout')
    else:
        messages.error(
            request, _("Ce panier n'existe pas"), extra_tags='alert-warning')
    return redirect('checkout')
