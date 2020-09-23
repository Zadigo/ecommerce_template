import csv
import functools
import itertools
import re
import secrets
from urllib.parse import urljoin

import pandas
from django.contrib.sites.shortcuts import get_current_site
from django.http.response import HttpResponse

AUTHORIZED_EXPORTS = ['current', 'all', 'collection']

AUTHORIZED_EXPORTS_FOR = ['general', 'facebook']

FACEBOOK_CATALOGUE_HEADER = [
    'id', 'title', 'description', 'condition', 'availability',
    'link', 'brand', 'price', 'image_link', 'google_product_category',
    'gender', 'is_final_sale', 'return_policy_days', 'inventory'
]

GENERAL_HEADER = ['id', 'name', 'description', 'price_pre_tax', 'active']


def autogenerate_name(prefix):
    return f'{prefix}_{secrets.token_hex(5)}.csv'

def validation_for_authorized(value):
    """
    Checks that a value is present in
    AUTHORIZED_EXPORTS
    """
    if value in AUTHORIZED_EXPORTS:
        return True
    return False


def validation_for_authorized_for(value):
    """
    Checks that a value is present in
    AUTHORIZED_EXPORTS_FOR
    """
    if value in AUTHORIZED_EXPORTS_FOR:
        return True
    return False


def all_validations(method, export_for):
    result1 = validation_for_authorized(method)
    result2 = validation_for_authorized_for(export_for)
    return all([result1, result2]) 


@functools.lru_cache(maxsize=5)
def general_iterator(request, queryset, brand, pandas_wrapper=False, *fields):
    """
    Creates a general purpose CSV object
    """
    rows = []
    for product in product:
        rows.append(
            [
                getattr(product, 'id'),
                getattr(product, 'name'),
                getattr(product, 'description'),
                getattr(product, 'price_pre_tax', 'To Improve'),
                getattr(product, 'active'),
                [getattr(product, field) for field in fields]
            ]
        )

    # Merges inner list with
    # outter list => [1, [2]]
    # becomes [1, 2]
    for row in rows:
        row = itertools.chain.from_iterable(row)
    return rows



@functools.lru_cache(maxsize=5)
def facebook_iterator(request, queryset, brand, pandas_wrapper=False):
    rows = []

    def build_url(product):
        if hasattr(product, 'get_absolute_url'):
            current_site = get_current_site(request)
            return urljoin(current_site, getattr(product, 'get_absolute_url'))

    def get_stock_state(product):
        if hasattr(product, 'in_stock'):
            state = getattr(product, 'in_stock')
            if state == True:
                return 'in stock'
            return 'out of stock'

    def get_price(product):
        field = None
        
        # First, attempt to return a
        # definition that returns a price
        if hasattr(product, 'get_price'):
            return getattr(product, 'get_price')()

        # Otherwise, try to get the first
        # field that starts with 'price'
        items = vars(product).keys()
        for key in items:
            if key.startswith('price'):
                field = key
                break
        if field:
            return getattr(product, field)
        raise AttributeError("Your model should have a price field from which we can extract the item's price")
    
    def get_main_images(product, single=True):
        # First, try to get a function
        # that returns an image marked
        # as being the main image for
        # the product
        if hasattr(product, 'get_main_image_url'):
            return getattr(product, 'get_main_image_url')
        else:
            if hasattr(product, 'images'):
                image = getattr('images').first()
                if hasattr(image, 'url'):
                    return image.url
                else:
                    raise AttributeError("The instance of the product's image does not have a url attribute")
            elif hasattr(product, 'image'):
                url = product.image
                if url.startswith('http'):
                    return url
                else:
                    raise TypeError(f"The image attribute of '{product.name}' does not return a valid url")
            else:
                raise AttributeError("Your product should reference an image or a set of images to choose from for the catalogue")
    
    def get_google_category(product):
        if hasattr(product, 'google_category'):
            return product.google_category
        else:
            raise AttributeError("Facebook catalogue requires a Google Category for the catalogue")
    
    for product in queryset:
        rows.append(
            [
                getattr(product, 'id'),
                getattr(product, 'name'),
                getattr(product, 'description'),
                'new',
                get_stock_state(product),
                build_url(product),
                brand,
                get_price(product),
                get_main_images(product),
                get_google_category(product),
                getattr(product, 'gender', 'female'),
                False,
                14,
                getattr(product, 'quantity', 10)
            ]
        )
    if pandas_wrapper:
        dataframe = pandas.DataFrame(rows)
        return dataframe
    return rows


def csv_http_response(request, queryset, brand, iterator=general_iterator):
    """
    Write a CSV HTTP response using an iterator
    """
    if not callable(iterator):
        raise TypeError("The iterator should be callable")

    rows = iterator(request, queryset, brand)
    if not isinstance(rows, list):
        raise TypeError("Your iterator should return valid rows")

    response = HttpResponse(context_type='text/csv')
    csv_writer = csv.writer(response)
    csv_writer.writerow(FACEBOOK_CATALOGUE_HEADER)
    csv_writer.writerows(rows)
    response['Content-Disposition'] = 'inline; filename=products.csv'
    return response

def import_csv(file_object, to_model):
    if file_object.name.endswith('csv'):
        rows = file_object.read()
        if not isinstance(rows, list):
            return False
        headers = rows.pop(0)
        dataframe = pandas.DataFrame(rows, columns=headers)
    else:
        return False
