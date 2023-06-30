from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    quantity = models.IntegerField()
    image = models.URLField()
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product_name


class UserMenu(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usermenu')
    favorites = models.ManyToManyField(Product, related_name='favorites')
    cart_items = models.ManyToManyField(Product, related_name='cart_items')

    def __str__(self):
        return f"{self.user.username}'s User Menu"
