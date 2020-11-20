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
        return reverse('shop:gender', args=['women'])


class MenShopSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1
    protocol = 'https'

    def items(self):
        return ['shop:gender']

    def location(self, viewname):
        return reverse('shop:gender', args=['men'])


class SizeGuideSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5
    protocol = 'https'

    def items(self):
        return ['shop:size_guide']


class SearchSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return ['shop:search']


class BaseProductsSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1
    protocol = 'https'
    category = None
    model = models.Product

    def get_queryset(self):
        return self.model.objects.filter(
            active=True, private=False
        )

    def items(self):
        queryset = self.get_queryset()
        return queryset.filter(collection__view_name=self.category)

    def lastmod(self, item):
        return item.last_modified
