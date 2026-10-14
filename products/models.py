from django.db import models
from django.template.backends import django
import django.core.validators

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    space_per_unit = models.PositiveIntegerField(
        validators=[django.core.validators.MinValueValidator(1)],
    )
    categories = models.ManyToManyField(Category, related_name='products', blank=True)

    def __str__(self):
        return f"{self.name} (SKU: {self.sku})"