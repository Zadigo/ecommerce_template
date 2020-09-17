import random
import string

from django.conf import settings


def create_discount_code():
    n = random.randrange(1000, 9000)
    s = random.choice(string.ascii_uppercase)
    return f'NAW{n}{s}'
