from django.db import models

class Community(models.Model):

    name = models.CharField(max_length=256)
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.CharField(max_length=256, editable=False)
