from django.db import models


class Need(models.Model):
    title = models.CharField(max_length=256)
