from django.db import models

# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products', blank=True, null=True)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Cart(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    total_price = models.FloatField(default=0)
    quantity = models.IntegerField(default=0)
    # is_bought


class OrderStatus(models.TextChoices):
    INITIAL = 'initial', "INITIAL"
    IN_PROGRESS = 'in_progress', "IN_PROGRESS"
    COMPLETED = 'completed', "COMPLETED"


class Order(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='order')
    address = models.CharField(max_length=255)

    status = models.CharField(max_length=50, choices=OrderStatus.choices)
