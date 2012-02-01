from django.db import models

class Community(models.Model):

    name = models.CharField(max_length=256)
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.SlugField(max_length=256)

    population = models.IntegerField()  # number of inhabitants
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    address = models.CharField(max_length=1024)
