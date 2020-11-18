from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from shop import models


class ShopSitemap(Sitemap):
    """Returns all the products from the shop"""
    changefreq = 'monthly'
    priority = 1
    protocol = 'https'

    def items(self):
        return ['shop:home']

    def location(self, view):
        return reverse(view)


class WomenShopSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1
    protocol = 'https'

    def items(self):
        return ['shop:gender']

    def location(self, viewname):
        return reverse('shop:gender', args=['femme'])


class MenShopSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1
    protocol = 'https'

    def items(self):
        return ['shop:gender']

    def location(self, viewname):
        return reverse('shop:gender', args=['homme'])


class BaseProductsSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1
    protocol = 'https'
    category = None
    model = models.Product
    queryset = models.Product.objects.filter(active=True, private=False)

    def lastmod(self, item):
        return item.last_modified


class Chaussures(BaseProductsSitemap):
    category = 'chaussures'

    def items(self):
        return self.queryset.filter(collection__view_name=self.category)


class Pantalons(Sitemap):
    changefreq = 'daily'
    priority = 1
    protocol = 'https'

    def items(self):
        return models.Product.objects.filter(collection__view_name='pantalons')

    def lastmod(self, product):
        return product.last_modified


class Robes(Sitemap):
    changefreq = 'daily'
    priority = 1
    protocol = 'https'

    def items(self):
        return models.Product.objects.filter(collection__view_name='robes')

    def lastmod(self, product):
        return product.last_modified


class Tops(Sitemap):
    changefreq = 'daily'
    priority = 1
    protocol = 'https'

    def items(self):
        return models.Product.objects.filter(collection__view_name='tops')

    def lastmod(self, product):
        return product.last_modified
