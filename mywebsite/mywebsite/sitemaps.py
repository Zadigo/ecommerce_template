from customercare.sitemap import CustomerCareSitemap
from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from hero.sitemap import HomeSitemap
from legal.sitemap import LegalSitemap
from shop.sitemap import BaseProductsSitemap


class Chaussures(BaseProductsSitemap):
    category = 'chaussures'


class Pantalons(BaseProductsSitemap):
    category = 'pantalons'


class Robes(BaseProductsSitemap):
    category = 'robes'


class Tops(BaseProductsSitemap):
    category = 'tops'


SITEMAPS = {
    'HomeSitemap': HomeSitemap,
    'LegalSitemap': LegalSitemap,
    'CustomerCareSitemap': CustomerCareSitemap,

    # 'ShopGenderSitemap': WomenShopSitemap,
    # 'MenShopSitemap': MenShopSitemap,

    'Chaussures': Chaussures,
    'Pantalons': Pantalons,
    'Robes': Robes,
    'Tops': Tops
}
