from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from shop import models


class HomeSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)

class ShopSitemap(Sitemap):
    """Returns all the products from the shop"""
    changefreq = 'monthly'
    priority = 1
    protocol = 'https'

    def items(self):
        return ['shop']

    def location(self, view):
        return reverse(view)

class WomenShopSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1
    protocol = 'https'

    def items(self):
        return ['shop_gender']

    def location(self, viewname):
        return reverse('shop_gender', args=['femme'])

class MenShopSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1
    protocol = 'https'

    def items(self):
        return ['shop_gender']

    def location(self, viewname):
        return reverse('shop_gender', args=['homme'])

class Chaussures(Sitemap):
    changefreq = 'daily'
    priority = 1
    protocol = 'https'

    def items(self):
        return models.Product.objects.filter(collection__view_name='chaussures')

    def lastmod(self, product):
        return product.last_modified

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

class LegalSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.2
    protocol = 'https'

    def items(self):
        return ['cgv', 'cgu', 'confidentialite']

    def location(self, item):
        return reverse(item)

class WhoAreWeSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.4
    protocol = 'https'

    def items(self):
        return ['who_are_we']

    def location(self, item):
        return reverse(item)

class CustomerCareSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.2
    protocol = 'https'

    def items(self):
        return ['customer_care', 'contact_us']

    def location(self, item):
        return reverse(item)

SITEMAPS = {
    'HomeSitemap': HomeSitemap,
    'LegalSitemap': LegalSitemap,
    'ShopGenderSitemap': WomenShopSitemap,
    'MenShopSitemap': MenShopSitemap,
    'WhoAreWeSitemap': WhoAreWeSitemap,
    'CustomerCareSitemap': CustomerCareSitemap,

    'Chaussures': Chaussures,
    'Pantalons': Pantalons,
    'Robes': Robes,
    'Tops': Tops
}
