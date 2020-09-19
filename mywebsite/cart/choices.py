from django.db import models

class Countries(models.Choices):
    FRANCE = 'Frane'
    BELGIQUE = 'Belgique'

class Cities(models.Choices):
    ILE_DE_FRANCE = 'Île de France',
    NORD = 'Nord'
    PACA = 'PACA'
    RHONE_ALPES = 'Rhônes Alpes'
