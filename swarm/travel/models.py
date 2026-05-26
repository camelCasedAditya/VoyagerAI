from django.db import models

# Model to store the query for which the trip was generated for and the outputted markdown
class Trip(models.Model):
    query = models.TextField()
    result = models.TextField()