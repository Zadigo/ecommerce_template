from django.conf import settings
from django.contrib.syndication.views import Feed
from django.shortcuts import reverse

from shop import models

class BaseFeed(Feed):
    author_email = 'contact.mywebsite@gmail.com'
    author_name = 'MyWebsite'
    language = 'fr'

class LatestWomensTops(BaseFeed):
    link = '/collection/femme/tops'

    def items(self):
        return models.ProductCollection.collection_manager.active_products('tops')

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_extra_kwargs(self, item):
        return {'price_pre_tax': item.price_pre_tax}
