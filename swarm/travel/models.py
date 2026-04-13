from django.db import models

# Create your models here.
class Trip(models.Model):
    query = models.TextField()
    result = models.TextField()