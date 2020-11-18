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

import json
import random

from cart import models as cart_models
from django import http, shortcuts
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import cache, paginator
from django.db import transaction
from django.db.models.aggregates import Avg
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from reviews.models import Review

from shop import models, serializers, sizes, tasks, utilities


@method_decorator(cache_page(60 * 30), name='dispatch')
class IndexView(generic.View):
    """Base view for the website's shop"""
    def get(self, request, *args, **kwargs):
        return render(request, 'pages/shop.html')


class LookBookView(generic.TemplateView):
    """Base view for the website's lookbook"""
    template_name = 'pages/lookbook.html'


class ShopGenderView(generic.View):
    """Base view for discovering the website's shop
    by category e.g. gender
    """
    def get(self, request, *args, **kwargs):
        collections = models.Collection.objects.filter(gender=kwargs['gender'])
        context = {
            'collections': collections[:3]
        }
        return render(request, 'pages/shop_gender.html', context)


class ProductsView(generic.ListView):
    """Main product's page"""
    model = models.Collection
    template_name = 'pages/collections.html'
    context_object_name = 'products'
    paginate_by = 12
    ordering = '-created_on'

    def get_queryset(self, **kwargs):
        collection_name = self.kwargs['collection']
        gender = self.kwargs['gender']

        try:
            collection = models.Collection.objects.get(view_name__exact=collection_name, gender=gender)
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

        collection = self.model.objects.get(
            view_name__exact=self.kwargs['collection'], 
            gender=self.kwargs['gender']
        )
        context['collection'] = collection
        return context


@method_decorator(cache_page(60 * 15), name='dispatch')
class ProductView(generic.DetailView):
    """View the details of a given product"""
    model = models.Product
    template_name = 'pages/product.html'
    context_object_name = 'product'

    def post(self, request, **kwargs):
        data = {'state': False}
        product = super().get_object()
        # TODO: Add a method function that prevent
        # triggering the rest of the method with 
        # any kinds of post requests
        cart = cart_models.Cart.cart_manager.add_to_cart(request, product)
        if cart:
            data.update({'state': True})
        else:
            messages.error(
                request, 
                "Une erreur s'est produite - ADD-CA", 
                extra_tags='alert-danger'
            )
        return JsonResponse(data=data)

    def get_queryset(self, **kwargs):
        queryset = self.model.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = super().get_object()

        serialized_product = serializers.ProductSerializer(instance=product)
        context['vue_product'] = serialized_product.data

        suggested_products = self.model.objects\
                                .prefetch_related('images') \
                                    .filter(active=True).exclude(id=product.id)[:3]
        context['more'] = suggested_products
        context['has_liked'] = False
        if self.request.user.is_authenticated:
            likes = models.Like.objects.filter(
                product=product, user=self.request.user)
            if likes.exists():
                context.update({'has_liked': True})

        reviews = Review.objects.reviews(product.id)
        context['reviews'] = reviews
        context['reviews_avg'] = reviews.aggregate(Avg('rating'))
        return context


class PreviewProductView(LoginRequiredMixin, generic.DetailView):
    """
    This is a custom view for previewing a product
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
    This is a special custom viewing a product in a non
    classified manner and one that does not appear in the
    urls of the main site --; this can be perfect for testing
    a product from a marketing perspective
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
        cart = cart_models.Cart.cart_manager.add_to_cart(request, product)
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


class SearchView(generic.ListView):
    """Main page for displaying product searches"""
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
        return context


@method_decorator(cache_page(3600 * 60), name='dispatch')
class SizeGuideView(generic.TemplateView):
    """View for providing the customer with information
    on sizes etc."""
    template_name = 'pages/size_guide.html'


@require_POST
@transaction.atomic
def add_like(request, **kwargs):
    product = get_object_or_404(models.Product, id=kwargs['pk'])
    data = {
        'product': product
    }
    if request.user.is_authenticated:
        data['user'] = request.user
        likes = models.Like.objects.filter(user=request.user)
        if product in likes:
            return JsonResponse(data={'state': False})
    models.Like.objects.create(**data)
    return JsonResponse(data={'state': True})


@require_POST
def size_calculator(request):
    """Calcultes from customer's measurements
    the correct size for him/her"""
    data = json.loads(request.body)
    bust = data['bust']
    chest = data['chest']
    if bust is None and chest is None:
        return JsonResponse(data={'state': False})

    bust = int(bust)
    chest = int(chest)
    calculator = sizes.BraCalculator(bust, chest)
    data = {
        'state': True, 
        'result': calculator.get_full_bra_size,
        'size': calculator.size, 
        'cup': calculator.cup
        }
    return JsonResponse(data=data)
