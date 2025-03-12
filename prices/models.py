from django.db import models

class Price(models.Model):
    ticket = models.CharField(max_length=10)
    price = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)