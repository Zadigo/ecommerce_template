from django.db.models import Choices


class ValueTypes(Choices):
    PERCENTAGE = 'percentage'
    FIXED_AMOUNT = 'fixed amount'
    FREE_SHIPPING = 'free shipping'
