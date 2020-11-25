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
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import cache, paginator
from django.db import transaction
from django.db.models.aggregates import Avg
from django.http.response import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView, View

from shop import models, serializers, sizes, tasks, utilities


def create_vue_products(queryset):
    items = []
    for product in queryset:
        images = product.images
        variant = product.variant
        base = {
            'id': product.id,
            'reference': product.reference,
            'url': product.get_absolute_url(),
            'collection': {
                'name': product.collection.name
            },
            'name': product.name,
            'price': str(product.get_price()),
            'main_image': product.get_main_image_url,
            'images': list(images.values('id', 'name', 'url', 'web_url', 'variant', 'main_image')),
            'variant': list(variant.values('id', 'name', 'verbose_name', 'in_stock', 'active')),
            'in_stock': product.in_stock,
            'our_favorite': product.our_favorite,
            'is_discounted': product.is_discounted,
            'price_pre_tax': str(product.price_pre_tax),
            'discounted_price': str(product.discounted_price),
            'slug': product.slug
        }
        items.append(base)
    return items


@method_decorator(cache_page(60 * 30), name='dispatch')
class IndexView(View):
    """Base view for the website's shop"""
    def get(self, request, *args, **kwargs):
        return render(request, 'pages/shop.html')


@method_decorator(cache_page(60 * 15), name='dispatch')
class ShopGenderView(View):
    """Base view for discovering the website's shop
    by category e.g. gender
    """
    def get(self, request, *args, **kwargs):
        context = {}
        gender = kwargs.get('gender')
        collections = models.Collection.objects.filter(
            gender=gender.title()
        )
        if collections.exists():
            context = {'collections': collections[:3]}
        return render(request, 'pages/shop_gender.html', context)


class ProductsView(ListView):
    """Main product's page"""
    model = models.Collection
    template_name = 'pages/collections.html'
    context_object_name = 'products'
    paginate_by = 12
    ordering = '-created_on'

    def get_queryset(self, **kwargs):
        view_name = self.kwargs.get('collection')

        try:
            collection = self.model.objects.get(
                view_name__exact=view_name
            )
        except:
            raise Http404("La collection n'existe pas")
        else:
            queryset = collection.product_set.filter(
                active=True, private=False
            )
            
            category = self.request.GET.get('category', None)
            if category is None:
                return queryset

            authorized_categories = ['all', 'promos', 'favorites']
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
        context['current_active_page'] = self.request.GET.get('page', 1)

        klass = super().get_paginator(products, self.paginate_by)
        
        # serialized_products = serializers.ProductSerializer(
        #     instance=klass.object_list, 
        #     many=True
        # )
        # context['vue_products'] = serialized_products.data

        # When passing to another category, the previous
        # products are still in the cache which creates
        # an issue
        category = self.request.GET.get('category')
        # if category is not None:
        #     cache.cache.delete('vue_products')

        # Specific technique in order to include the
        # product url, main_image url and images
        # vue_products = cache.cache.get('vue_products', None)
        vue_products = create_vue_products(klass.object_list)
        # if vue_products is None:
            # cache.cache.set('vue_products', vue_products, timeout=1200)
        context['vue_products'] = json.dumps(vue_products)

        collection = self.model.objects.get(
            view_name__exact=self.kwargs.get('collection'),
            gender=self.kwargs.get('gender').title()
        )
        context['collection'] = collection
        return context


@method_decorator(cache_page(60 * 15), name='dispatch')
class ProductView(DetailView):
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
                product=product, user=self.request.user
            )
            if likes.exists():
                context.update({'has_liked': True})

        reviews = product.review_set.all()
        context['reviews'] = reviews
        context['reviews_avg'] = reviews.aggregate(Avg('rating'))
        return context


@method_decorator(never_cache, name='dispatch')
class PreviewProductView(LoginRequiredMixin, DetailView):
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
            return HttpResponseForbidden('You are not authorized on this page')
        return content

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = super().get_object()

        serialized_product = serializers.ProductSerializer(instance=product)
        context['vue_product'] = serialized_product.data
        return context


@method_decorator(cache_page(60 * 30), name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class PrivateProductView(DetailView):
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
            return JsonResponse(data={'success': 'success'})
        else:
            return JsonResponse(data={'failed': 'missing parameters'}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = super().get_object()

        serialized_product = serializers.ProductSerializer(instance=product)
        context['vue_product'] = serialized_product.data
        
        return context    


class SearchView(ListView):
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


@method_decorator(cache_page(60 * 60), name='dispatch')
class SizeGuideView(TemplateView):
    """View for providing the customer with information
    on sizes etc."""
    template_name = 'pages/size_guide.html'


@require_POST
@transaction.atomic
def add_like(request, **kwargs):
    data = {'state': False}
    product = get_object_or_404(models.Product, id=kwargs['pk'])
    if request.user.is_authenticated:
        likes = product.like_set.filter(user=request.user)
        if likes.exists():
            return JsonResponse(data=data)
        product.like_set.create(user=request.user)
    else: 
        redirect_url = f"{reverse('accounts:login')}?next={product.get_absolute_url()}"
        data.update({'redirect_url': redirect_url})
    return JsonResponse(data=data)


@require_POST
def size_calculator(request, **kwargs):
    """Calcultes from customer's measurements
    the correct size for him/her"""
    # data = json.loads(request.body)
    # bust = data['bust']
    # chest = data['chest']
    bust = request.POST.get('bust')
    chest = request.POST.get('chest')
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


@require_POST
@transaction.atomic
def add_review(request, **kwargs):
    data = {
        'state': False, 
        'message': "L'avis n'a pas pu être créé"
    }
    score = request.POST.get('score')
    text = request.POST.get('text')
    if request.user.is_authenticated:
        product = get_object_or_404(models.Product, id=kwargs.get('pk'))
        review = product.review_set.create(
            user=request.user, 
            text=text,
            rating=score
        )
        data.update({
            'state': True,
            'message': "Votre avis a été créé"
        })
    return JsonResponse(data=data)
