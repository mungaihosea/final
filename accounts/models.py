from django.db import models

class Feestructure(models.Model):
    term1 = models.IntegerField()
    term2 = models.IntegerField()
    term3 = models.IntegerField()

