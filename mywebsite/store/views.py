import json

from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from store import models
from store.utils import get_product_model

PRODUCT_MODEL = get_product_model()


def create_vue_products(queryset, using: list = []):
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
        using.append(base)
    return using


class BaseDetailView(DetailView):
    model = models.Store
    store_name_field = 'storename'
    context_object_name = 'products'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg)
        store_name = self.kwargs.get(self.store_name_field)

        if pk is not None and store_name is not None:
            queryset = queryset.filter(pk=pk, name=store_name)

        if pk is None and store_name is None:
            raise AttributeError('The store name and the primary key of the store should be provided')

        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


# @method_decorator(cache_page(60 * 15), name='dispatch')
class StoresView(ListView):
    model = models.Store
    template_name = 'pages/stores.html'
    context_object_name = 'stores'


class StoreView(ListView):
    model = models.Store
    template_name = 'pages/collections.html'
    context_object_name = 'products'
    paginate_by = 12
    ordering = '-created_on'

    def get_queryset(self):
        try:
            store = self.model.objects.get(pk=self.kwargs.get('pk'))
        except:
            return Http404("La boutique n'existe pas")
        else:
            products = cache.get('store_products', [])
            if not products:
                products = store.products.filter(active=True, private=False)
                cache.set('store_products', products, timeout=600)

            category = self.request.GET.get('category', None)
            if category is None:
                return products

            authorized_categories = ['all', 'promos', 'favorites']
            if category in authorized_categories:
                if category == 'all':
                    return products
                elif category == 'promos':
                    return products.filter(discounted=True)
                elif category == 'favorites':
                    return products.filter(our_favorite=True)
            return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_queryset()
        context['current_active_page'] = self.request.GET.get('page', 1)
        klass = super().get_paginator(products, self.paginate_by)

        category = self.request.GET.get('category')
        if category is not None:
            cache.cache.delete('vue_products')

        vue_products = cache.get('vue_products', [])

        if not vue_products:
            vue_products = create_vue_products(klass.object_list)
            cache.set('vue_products', vue_products, timeout=1200)
        context['vue_products'] = json.dumps(vue_products)
        return context


class StoreProductDetailView(BaseDetailView):
    model = models.Store
    template_name = 'pages/product.html'
    context_object_name = 'product'


@require_POST
def create_new_product(request, **kwargs):
    store = get_object_or_404(models.Store, id=kwargs.get('pk'))
    data = {}
    new_product = PRODUCT_MODEL.objects.create(**data)
    store.products.add(new_product)
