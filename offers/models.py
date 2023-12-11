from datetime import date

from django.db import models


# Create your models here.
class Offer(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    discount = models.PositiveIntegerField()
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    end_date = models.DateField()

    def __str__(self):
        return self.name

    def is_offer_expired(self):
        today = date.today()
        if self.end_date < today:
            return True
        else:
            return False
