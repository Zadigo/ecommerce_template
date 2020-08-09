import datetime
import hashlib
import itertools
import random
import secrets
import string

from django.core import exceptions


def create_transaction_token(n=1, salt='mywebsite'):
    """Create a payment token for Google enhanced ecommerce"""
    tokens = [secrets.token_hex(2) for _ in range(0, n)]
    # Append the salt that allows us to identify
    # if the payment method is a valid one
    tokens.append(hashlib.sha256(salt.encode('utf-8')).hexdigest())
    return '-'.join(tokens)


def validate_payment_id(token, salt='mywebsite'):
    """Validate a payment ID"""
    parts = token.split('-')
    hashed_salt = hashlib.sha256(salt.encode('utf-8')).hexdigest()
    
    # The salt should always theoretically
    # be the last component of the array
    incoming_hashed_part = parts.pop(-1)

    truth_array = []

    # Compare incoming salt to salt
    if hashed_salt == incoming_hashed_part:
        truth_array.append(True)
    else:
        truth_array.append(False)

    # We should only have 5
    # parts in the array outside
    # of the salt
    if len(parts) == 5:
        truth_array.append(True)
    else:
        truth_array.append(False)
    
    # Each part should have a
    # maximum of 5 characters
    for part in parts:
        if len(part) != 4:
            truth_array.append(False)

    return all(truth_array)


def create_reference(n=5, append_prefix=True):
    """Create a basic reference: `NAW201906126011b0e0b8`
    """
    current_date = datetime.datetime.now().date()
    token = secrets.token_hex(n)
    if append_prefix:
        prefix = f'NAW{current_date.year}{current_date.month}{current_date.day}'
        return prefix + token
    else:
        return token


def create_product_reference():
    """Creates a product reference number: AC4565ZE4TEZD
    """
    # Create two first letters ex. AC
    capital_letters = string.ascii_uppercase
    first = ''.join(random.choice(capital_letters) for _ in range(0, 2))
    # Get a number between 1000 and 9000
    second = random.randrange(1000, 9000)
    # Add a salt that makes sure the reference
    # is unique in every ways
    salt = secrets.token_hex(4).upper()
    return f'{first}{second}{salt}'


def create_slug(name):
    """Creates a product slug name"""
    names = name.split(' ')

    def normalize_names(raw_name):
        return raw_name.strip().lower()

    for name in names:
        names[names.index(name)] = normalize_names(name)

    return '-'.join(names)


def create_image_slug(name, reverse=False):
    """Create an image slug
    
    Example
    -------

        an_image_slug.jpg

    Parameters
    ----------

        reverse: from an image slug, guess the name of the image: an_image_slug 
        becomes in that case 'An image slug'
    """
    if reverse:
        if '_' in name:
            spaced_name = name.split('_')
            cleaned_name = [name.split('.') for name in spaced_name if '.' in name][0][0]
            spaced_name.pop(-1)
            spaced_name.append(cleaned_name)
            return ' '.join(spaced_name).capitalize()

    image_name = '_'.join(name.split(' '))
    return f'{image_name.strip().lower()}.jpg'
    
    
def create_cart_id(n=12):
    """Creates an iD for the Anonymous cart so that we can
    easily get all the items registered by an anonymous user
    in the cart.

    This iD is saved in the session and in the local storage.

    Description
    -----------

        2019_01_02_token
    """
    token = secrets.token_hex(n)
    date = datetime.datetime.now().date()
    return f'{date.year}_{date.month}_{date.day}_' + token


def calculate_discount(price, pct):
    """Calculates a discount price

    Formula
    -------
        price * (1 - (pct / 100))
    """
    try:    
        return round(float(price) * (1 - (pct / 100)), 2)
    except:
        raise exceptions.ValidationError('Price should be an integer or a float')

def calculate_tva(price, tva=20):
    """Calculates the tax on a product

    Formula
    -------
        price * (1 + (tax / 100))
    """
    return round(float(price) * (1 + (tva / 100)), 2)


def impressions_helper(queryset):
    """A helper function that helps create an impressions
    datalayer for a list of products
    """
    items = []
    position = 1
    try:
        for product in queryset:
            if product.discount_price > 0:
                price = product.discount_price
            else:
                price = product.price_ht

            items.append(
                {
                    'id': product.reference,
                    'name': product.name,
                    'price': price,
                    'brand': "Nawoka",
                    'category': product.collection.collection_name,
                    'position': position 
                }
            )
            position = position + 1
    except:
        return []
    return items


def add_to_current_date(d=15, use_timezone=False):
    """Adds d-days to a current date"""
    if use_timezone:
        from django.utils import timezone
        return timezone.now() + datetime.timedelta(days=d)
    current_date = datetime.datetime.now().date()
    return current_date + datetime.timedelta(days=d)


def get_image_name(image):
    if '.' in image:
        items = image.split('.')
    return items[0]


def create_product_slug(word:str):
    accents = {
        'é': 'e',
        'è': 'e',
        'ê': 'e',
        'ë': 'e',
        'à': 'a',
        'â': 'a',
        'ô': 'o',
        'ï': 'i',
        'î': 'i',
        'ù': 'u',
        'ü': 'u',
        'ç': 'c'
    }
    words_to_exlude = ['de', 'en', 'le', 'la']
    words = word.split(' ')

    intermediate_word = []
    for i in range(0, len(words)):
        if "d'" in words[i]:
            words[i] = words[i].replace("d'", ' ')
        if words[i] not in words_to_exlude:
            intermediate_word.append(words[i].strip().lower())
    
    final_word = '-'.join(intermediate_word)
    non_accentuated_word = ''
    for letter in final_word:
        try:
            non_accentuated_word = non_accentuated_word + accents[letter]
        except:
            non_accentuated_word = non_accentuated_word + letter            

    return non_accentuated_word

def create_discount_code():
    n = random.randrange(1000, 9000)
    s = random.choice(string.ascii_uppercase)
    return f'NAW{n}{s}'
