from django.contrib.syndication.views import Feed
from django.shortcuts import reverse

from django.conf import settings

from shop import models

class BaseFeed(Feed):
    author_email = settings.EMAIL_HOST_USER
    # author_name = settings

class LatestBags(BaseFeed):
    link = '/.../'
    language = 'fr'

    def items(self):
        return models.Product.product_manager

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.created_on

    def item_updateddate(self, item):
        return item.modified_on