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

# class CollectionSitemap(Sitemap):
#     """Returns the main product's categories"""
#     changefreq = 'weekly'
#     priority = 1
#     protocol = 'https'

#     def items(self):
#         return ['sacs', 'bottines', 'promos', 'favoris']

#     def location(self, viewname):
#         return reverse('product_collection', kwargs={'collection': viewname})

# class ShopSitemap(Sitemap):
#     """Returns all the products from the shop"""
#     changefreq = 'weekly'
#     priority = 1
#     protocol = 'https'

#     def items(self):
#         return models.Product.product_manager.active_products()

#     def location(self, product):
#         return product.get_absolute_url()

#     def lastmod(self, product):
#         return product.last_modified

# class Bags(Sitemap):
#     changefreq = 'daily'
#     priority = 1
#     protocol = 'https'

#     def items(self):
#         return models.Product.product_manager.in_collection_queryset('sacs')

#     def lastmod(self, product):
#         return product.last_modified

# class Watches(Sitemap):
#     changefreq = 'daily'
#     priority = 1
#     protocol = 'https'

#     def items(self):
#         return models.Product.product_manager.in_collection_queryset('montres')

#     def lastmod(self, product):
#         return product.last_modified

# class Bracelets(Sitemap):
#     changefreq = 'daily'
#     priority = 1
#     protocol = 'https'

#     def items(self):
#         return Product.product_manager.in_collection_queryset('bracelets')

#     def lastmod(self, product):
#         return product.last_modified

# class CGVSitemap(Sitemap):
#     changefreq = 'yearly'
#     priority = 0.2
#     protocol = 'https'

#     def items(self):
#         return ['cgv']

#     def location(self, item):
#         return reverse(item)

# class PrivacySitemap(Sitemap):
#     changefreq = 'yearly'
#     priority = 0.2
#     protocol = 'https'

#     def items(self):
#         return ['confidentialite']

#     def location(self, item):
#         return reverse(item)

# class ContactUsSitemap(Sitemap):
#     changefreq = 'monthly'
#     priority = 0.2
#     protocol = 'https'

#     def items(self):
#         return ['contact_us']

#     def location(self, item):
#         return reverse(item)

# class WhoAreWeSitemap(Sitemap):
#     changefreq = 'monthly'
#     priority = 0.4
#     protocol = 'https'

#     def items(self):
#         return ['who_are_we']

#     def location(self, item):
#         return reverse(item)

# class CustomerCareSitemap(Sitemap):
#     changefreq = 'monthly'
#     priority = 0.2
#     protocol = 'https'

#     def items(self):
#         return ['customer_care', 'contact_us']

#     def location(self, item):
#         return reverse(item)

# SITEMAPS = {
#     'HomeSitemap': HomeSitemap,
#     'CollectionSitemap': CollectionSitemap,
#     'ShopSitemap': ShopSitemap,
#     # 'Watches': Watches,
#     # 'Bracelets': Bracelets,
#     'CGVSitemap': CGVSitemap,
#     'PrivacySitemap': PrivacySitemap,
#     'CustomerCareSitemap': CustomerCareSitemap,
#     'ContactUsSitemap': ContactUsSitemap,
#     'WhoAreWeSitemap': WhoAreWeSitemap
# }
