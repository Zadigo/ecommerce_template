from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from customercare.sitemap import CustomerCareSitemap
from hero.sitemap import HomeSitemap
from legal.sitemap import LegalSitemap
from shop import models
from shop.sitemap import (Chaussures, MenShopSitemap, Pantalons, Robes, Tops,
                          WomenShopSitemap)

SITEMAPS = {
    'HomeSitemap': HomeSitemap,
    'LegalSitemap': LegalSitemap,

    'ShopGenderSitemap': WomenShopSitemap,
    'MenShopSitemap': MenShopSitemap,
    'CustomerCareSitemap': CustomerCareSitemap,

    'Chaussures': Chaussures,
    'Pantalons': Pantalons,
    'Robes': Robes,
    'Tops': Tops
}
