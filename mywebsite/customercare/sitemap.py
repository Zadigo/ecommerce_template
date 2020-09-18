from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse


class CustomerCareSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.2
    protocol = 'https'

    def items(self):
        return ['customer_care:home']

    def location(self, item):
        return reverse(item)
