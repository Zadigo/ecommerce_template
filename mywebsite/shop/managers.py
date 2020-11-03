import datetime
import re

from django import http
from django.contrib import messages
from django.core import exceptions
from django.db.models import (Avg, Case, Count, F, Q, QuerySet, Sum, When,
                              fields)
from django.db.models.functions import TruncMonth

from shop import utilities


class CollectionManager(QuerySet):
    def active_products(self, collection_name):
        collection = self.get(name__iexact=collection_name)
        return collection.product_set.filter(active=True)

    def products_between_price(self, collection_name, a, b):
        products = self.active_products(collection_name)
        price_between_a_and_b = Q(price_pre_tax__gt=a) & Q(price_pre_tax__lt=b)
        return products.filter(price_between_a_and_b)


class ProductManager(QuerySet):
    def active_products(self):
        return self.filter(active=True, private=False)

    def private_products(self):
        return self.filter(private=True)
        
    def count_products_by_collection(self):
        """Returns the count of products by collection"""
        products = self.values('collection__name')
        items = products.annotate(count_of=Count('name'))
        return [[item['collection__name'] for item in items], [item['count_of'] for item in items]]

    def average_price_by_collection(self):
        """Returns the average price by collection"""
        products = self.values('collection__name')
        return products.order_by('collection__name')\
                        .annotate(average_price=Count('price_pre_tax'))

    def search_product(self, searched_item):
        """
        Allows the user to search for a product on
        the website
        """
        qfunctions = Q(name__icontains=searched_item) | Q(
            collection__name__icontains=searched_item)
        queryset = self.filter(qfunctions).filter(active=True)
        if queryset.exists():
            return queryset
        return []

    def advanced_search(self, searched_terms):
        """
        This is an advanced search feature for the dashboard
        for example
        """
        queryset = self.all()

        if ':' in searched_terms:
            key, value = searched_terms.split(':')
            if key == 'state':
                if value == 'actif' \
                    or value == 'true' \
                        or value == 'True':
                    return queryset.filter(active=True)
                elif value == 'inactif' \
                    or value == 'false' \
                        or value == 'False':
                    return queryset.filter(active=False)

        if searched_terms.startswith('-'):
            searched_terms = re.search(r'^-(?:\s?)(.*)', searched_terms).group(1)
            searched_terms = ~Q(name__icontains=searched_terms) & ~Q(reference__icontains=searched_terms) \
                            & ~Q(collection__name__icontains=searched_terms)
        else:
            searched_terms = Q(name__icontains=searched_terms) | Q(reference__icontains=searched_terms) \
                            | Q(collection__name__icontains=searched_terms)

        return queryset.filter(searched_terms)

    def to_be_published_today(self):
        """Return a queryset of products that are
        not published on the current date"""
        current_date = datetime.datetime.now()
        products = self.filter(to_be_published_on__date=current_date, active=False)
        return products

    def out_of_stock(self, threshold=5):
        """Return a queryset of products that are
        out of stock or nearly out of stock"""
        logic = (
            Q(active=True) &
            Q(monitor_quantity=True) &
            Q(quantity__lte=threshold)
        )
        return self.filter(logic)
        

##############
#
# DASHBOARD
#
##############

class BaseStatistics(QuerySet):
    def total_count(self):
        return self.all().count()

