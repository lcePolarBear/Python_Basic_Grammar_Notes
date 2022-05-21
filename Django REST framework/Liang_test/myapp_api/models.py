from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    sex = models.CharField(max_length=10)
    age = models.IntegerField()