from django.db import models

class StoreCurrencies(models.Choices):
    EUR = 'eur'
    DOLLARS = 'dollars'

class IndustryChoices(models.Choices):
	FASHION = 'Fashion'
	CLOTHING = 'clothing'
	JEWELRY = 'jewelry'
