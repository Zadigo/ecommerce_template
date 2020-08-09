from django.db import models


class FirstConditionChoices(models.Choices):
    NOM_DU_PRODUIT = 'Nom du produit'
    PRIX = 'Prix'


class SecondConditionsChoices(models.Choices):
    IS_EQUAL_TO = 'is equal to'
    IS_NOT_EQUAL_TO = 'is not equal to'
    IS_GREAT_THAN = 'is greater than'
    IS_LESS_THAN = 'is less than'
    STARTS_WITH = 'starts with'
    ENDS_WITH = 'ends with'
    CONTAINS = 'contains'
    DOES_NOT_CONTAIN = 'does not contain'
    YES = 'yes'
    NO = 'no'
