from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse


class LegalSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.4
    protocol = 'https'

    def items(self):
        return ['legal:use', 'legal:sale', 'legal:privacy', 'legal:who_we_are']

    def location(self, item):
        return reverse(item)
