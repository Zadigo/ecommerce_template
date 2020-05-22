"""

    Tunnel
    ------

        checkout > shipment > payment > success
"""

from django import http, shortcuts
from django.core import paginator
from django.core import serializers as core_serializers
from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators import http as http_decorator
from django.views.decorators.csrf import csrf_exempt

from shop import models, payment_logic, serializers


def no_cart_router(request, current_path, debug=False):
    if not debug:
        try:
            request.session['cart_id']
        except:
            return redirect(reverse('no_cart'))
        return redirect(reverse(current_path))
    else:
        return render

class IndexView(generic.View):
    def get(self, request, *args, **kwargs):
        context = {
            'collections': models.ProductCollection.objects.all()
        }
        return render(request, 'pages/shop.html', context)

class ProductsView(generic.ListView):
    model = models.ProductCollection
    template_name = 'pages/collections.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self, **kwargs):
        collection_name = self.kwargs['collection']
        products = models.ProductCollection.objects.get(view_name__exact=collection_name).product_set.all()
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        klass = super().get_paginator(self.queryset, self.paginate_by)

        collection_name = self.kwargs['collection']
        context['collection'] = models.ProductCollection.objects.get(view_name__exact=collection_name)

        serialized_products = serializers.ProductSerializer(instance=klass.object_list, many=True)
        context['vue_products'] = serialized_products.data
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
        return context

class CheckoutView(generic.ListView):
    model = models.Cart
    template_name = 'pages/cart.html'
    context_object_name = 'constructed_products'

    def post(self, request, **kwargs):
        return http.JsonResponse({'success': 'success'})
    
    def get_queryset(self, **kwargs):
        cart_id = self.request.session.get('cart_id')
        return models.Cart.cart_manager.cart_products(cart_id)

    def get_context_data(self):
        context = super().get_context_data()
        context['vue_products'] = self.get_queryset()
        return context    

class CartSuccessView(generic.TemplateView):
    template_name = 'pages/success.html'

    def get(self, request, *args, **kwargs):
        return no_cart_router(request, reverse('success'), debug=True)(request, self.template_name)

class ShipmentView(generic.ListView):
    model = models.Cart
    template_name = 'pages/shipment.html'
    context_object_name = 'products'

    def get_queryset(self, **kwargs):
        cart_id = self.request.session.get('cart_id')
        return models.Cart.cart_manager.cart_products(cart_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id')
        context['cart_id'] = cart_id
        context['cart_total'] = self.model.cart_manager.cart_total(cart_id)['cart_total']
        return context

class PaymentView(generic.ListView):
    model = models.Cart
    template_name = 'pages/payment.html'
    context_object_name = 'products'

    def get_queryset(self, **kwargs):
        cart_id = self.request.session.get('cart_id')
        return models.Cart.cart_manager.cart_products(cart_id)

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        cart_id = self.request.session.get('cart_id')
        context['cart_id'] = cart_id
        context['cart_total'] = self.model.cart_manager.cart_total(cart_id)['cart_total']
        return context

    def post(self, request, **kwargs):
        user_infos = payment_logic.UserInfosHelper(request)
        context = self.get_context_data(object_list=self.get_queryset(), **kwargs)
        context.update({'user_infos': user_infos.get_user_infos})
        return render(request, self.template_name, context)

@http_decorator.require_http_methods(['POST'])
def payment_process(request, **kwargs):
    stripe_token = request.POST.get('token')
    user_infos = {}
    logic = payment_logic.ProcessPayment(request, stripe_token, user_infos)
    return logic.payment_processor(payment_debug_mode=True)

class EmptyCartView(generic.TemplateView):
    template_name = 'pages/no_cart.html'

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
            return http.HttpResponseForbidden('Could not identify.')

    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = shortcuts.get_object_or_404(models.Cart, cart_id=cart_id, pk=kwargs['pk'])
        if cart:
            quantity = cart.quantity

            if kwargs['method'] == 'add':
                quantity = quantity + 1
            else:
                quantity = quantity - 1

            if quantity < 1:
                cart.delete()
                try:
                    shortcuts.get_list_or_404(models.Cart, cart_id=cart_id)
                except:
                    return redirect('checkout')
                else:
                    return redirect('no_cart')

            cart.quantity = quantity
            cart.save()
        return redirect('checkout')
    return redirect('checkout')
