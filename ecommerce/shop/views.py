"""

    Conversion Tunnel
    ------

        checkout > shipment > payment > success

    Payment process
    -------

        1. On submitting the form, an AJAX request is
           done using Stripe in order to get the token

        2. An intermediate view is used afterwards to
           process the payment on the backend side

        3. If the payment was successful, a redirect is
           done to the SuccessView
"""

import random
from ast import literal_eval

from django import http, shortcuts
from django.contrib import messages
from django.core import exceptions, paginator
from django.core import serializers as core_serializers
from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators import http as http_decorator
from django.views.decorators.csrf import csrf_exempt

from accounts import models as accounts_models
from shop import forms, models, payment_logic, serializers, utilities


def no_cart_router(request, current_path, debug=False):
    if not debug:
        try:
            request.session['cart_id']
        except:
            return redirect(reverse('no_cart'))
        return redirect(reverse(current_path))
    else:
        return render

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


class IndexView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'pages/shop.html')

class LookBookView(generic.TemplateView):
    template_name = 'pages/lookbook.html'

class ShopGenderView(generic.View):
    def get(self, request, *args, **kwargs):
        collections = models.Collection.objects.filter(gender=kwargs['gender'])
        context = {
            'collections': collections[:3]
        }
        return render(request, 'pages/shop_gender.html', context)

class ProductsView(generic.ListView):
    model = models.Collection
    template_name = 'pages/collections.html'
    context_object_name = 'products'
    paginate_by = 12
    ordering = '-created_on'

    def get_queryset(self, **kwargs):
        collection_name = self.kwargs['collection']
        gender = self.kwargs['gender']

        try:
            products = models.Collection.objects.get(view_name__exact=collection_name, gender=gender)
        except:
            # TODO: When the collection does not exist,
            # instead of returning a hard error 500,
            # redirect the user to another screen
            pass
        else:
            queryset = products.product_set.filter(active=True)
        finally:
            authorized_categories = ['all', 'promos', 'favorites']
            category = self.request.GET.get('category')
            if not category or category == '':
                category = 'all'
            if category in authorized_categories:
                category = authorized_categories[authorized_categories.index(category)]
                if category == 'all':
                    pass
                elif category == 'promos':
                    queryset = queryset.filter(discounted=True)
                elif category == 'favorites':
                    queryset = queryset.filter(our_favorite=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_queryset(**kwargs)

        # Set a specific pagination number to
        # active depending on which page we are
        current_active_page = self.request.GET.get('page')
        if not current_active_page:
            current_active_page = 1
        context['current_active_page'] = current_active_page

        klass = super().get_paginator(products, self.paginate_by)
        
        serialized_products = serializers.ProductSerializer(instance=klass.object_list, many=True)
        context['vue_products'] = serialized_products.data

        collection = self.model.objects.get(view_name__exact=self.kwargs['collection'], gender=self.kwargs['gender'])
        context['collection'] = collection

        context['impressions'] = create_products_impressions(products)
        return context

@method_decorator(csrf_exempt, name='dispatch')
class ProductView(generic.DetailView):
    model = models.Product
    queryset = models.Product.objects.all()
    template_name = 'pages/product.html'
    context_object_name = 'product'

    def post(self, request, **kwargs):
        product = super().get_object()
        
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

@http_decorator.require_http_methods(['GET'])
def delete_product_from_cart(request, **kwargs):
    cart_id = request.session.get('cart_id')
    if cart_id:
        product = shortcuts.get_object_or_404(models.Cart, cart_id=cart_id, pk=kwargs['pk'])
        if product:
            product.delete()
            try:
                shortcuts.get_list_or_404(models.Cart)
            except:
                return redirect('checkout')
            else:
                return redirect('no_cart')
    return redirect('checkout')

@http_decorator.require_http_methods(['GET'])
def alter_item_quantity(request, **kwargs):
    accepted_methods = ['add', 'reduce']
    if 'method' in kwargs:
        if kwargs['method'] not in accepted_methods:
            messages.error(request, "Quelque chose c'est mal passé - CX-ATOC", extra_tags='alert-error')

    cart_id = request.session.get('cart_id')
    if cart_id:
        method = kwargs['method']
        user_carts = models.Cart.objects.filter(cart_id=cart_id)
        try:
            cart_to_alter = user_carts.get(id=kwargs['pk'])
        except:
            messages.error(request, "Le panier n'existe pas", extra_tags='alert-warning')
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
        messages.error(request, "Ce panier n'existe pas.", extra_tags='alert-warning')
    return redirect('checkout')

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
        request.session['user_infos'] = {}
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
        import ast
        stripe_token = request.POST.get('token')
        user_infos = request.session.get('user_infos')
        request.session['conversion'] = {'reference': '', 'transaction': '', 'payment': ''}
        return http.JsonResponse(data={'status': False})

class CartSuccessView(generic.TemplateView):
    template_name = 'pages/success.html'

    def get(self, request, *args, **kwargs):
        context = {}
        reference = request.session.get('conversion')['reference']
        transaction = request.session.get('conversion')['transaction']
        url_based_token = request.GET.get('transaction_token')
        session_based_token = request.session.get('transaction_token')

        # None == None is True and to counter this effect,
        # this logic checks that both values are indeed present
        if url_based_token is None and session_based_token is None:
            return redirect(reverse('no_cart'))

        if url_based_token == session_based_token:
            customer_order = models.CustomerOrder.objects.get(reference=reference)
            if customer_order:
                products = customer_order.cart.all()
                context['products'] = creat_cart_products_from_queryset(products)
            context['reference'] = reference
            context['transaction'] = transaction
            context['payment'] = request.session.get('conversion')['payment'] or 0
            return render(request, 'pages/success.html', context=context)
        else:
            return redirect(reverse('no_cart'))

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
        collection = models.Collection.objects.get(view_name=random_collection)
        proposed_products = collection.product_set.all()[:4]
        context['proposed_products'] = proposed_products

        context['impressions'] = create_products_impressions(products)
        return context

@http_decorator.require_http_methods('GET')
def csv_catologue(request):
    import csv
    products = models.Collection\
                    .collection_manager.active_products('tops')

    rows = []
    response = http.HttpResponse(content_type='text/csv')
    csv_writer = csv.writer(response)
    csv_writer.writerow(['id', 'title', 'description', 'condition', 
                'availability', 'link', 'brand', 'price', 
                        'image_link', 'google_product_category'])
    for product in products:
        url = f'https://nawoka.fr{product.get_absolute_url()}'
        rows.append([product.id, product.name, product.description, 'new', 'in stock',
                        url, 'Nawoka', product.get_price(),
                            product.get_main_image_url, 178])
    csv_writer.writerows(rows)

    response['Content-Disposition'] = 'inline; filename=products.csv'
    return response
  
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
