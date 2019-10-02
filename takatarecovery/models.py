from django.db import models
from django.utils import timezone
from django.urls import reverse


class takatarecovery(models.Model):
    vin = models.CharField(max_length=50, null=True)
    business_name = models.TextField(null=True)
    contact_no = models.IntegerField(null=True)
    email = models.EmailField(null=True)
    date = models.DateField(null=True)
    source = models.CharField(max_length=10, null=True)

    def __str__(self):
        return '{} at {}'.format(self.vin)

class makemodel(models.Model):
    oem = models.TextField(null=True)
    model = models.TextField(null=True)
    note = models.TextField(null=True)
    year = models.TextField(null=True)
    airbag = models.TextField(null=True)
    status = models.TextField(null=True)

    def __str__(self):
        return '{} at {}'.format(self.oem)
