from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse


class HomeSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return ['hero:home']

    def location(self, item):
        return reverse(item)
