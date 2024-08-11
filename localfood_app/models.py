from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404


class User(AbstractUser):
    is_buyer = models.BooleanField('buyer status', default=False)
    is_seller = models.BooleanField('seller status', default=False)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=False, blank=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_primary_image(self):
        return self.productimage_set.first()


class ProductImage(models.Model):
    file_path = models.ImageField(upload_to='product_image/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)


class Address(models.Model):
    PROVINCE_CHOICES = (
        ('Dolnośląskie', 'Dolnośląskie'),
        ('Kujawsko-pomorskie', 'Kujawsko-pomorskie'),
        ('Lubelskie', 'Lubelskie'),
        ('Lubuskie', 'Lubuskie'),
        ('Łódzkie', 'Łódzkie'),
        ('Małopolskie', 'Małopolskie'),
        ('Mazowieckie', 'Mazowieckie'),
        ('Opolskie', 'Opolskie'),
        ('Podkarpackie', 'Podkarpackie'),
        ('Podlaskie', 'Podlaskie'),
        ('Pomorskie', 'Pomorskie'),
        ('Śląskie', 'Śląskie'),
        ('Świętokrzyskie', 'Świętokrzyskie'),
        ('Warmińsko-mazurskie', 'Warmińsko-mazurskie'),
        ('Wielkopolskie', 'Wielkopolskie'),
        ('Zachodniopomorskie', 'Zachodniopomorskie'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    city = models.CharField(max_length=100)
    street_name = models.CharField(max_length=100, null=True, blank=True)
    street_number = models.CharField(max_length=100, null=True, blank=True)
    apartment_number = models.CharField(max_length=100, null=True, blank=True)
    unit_number = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=20, choices=PROVINCE_CHOICES, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    realization_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    is_realized = models.BooleanField(default=False)


    def calculate_total_price(self):
        return self.product.price * self.quantity

    @classmethod
    def add_product_to_basket(cls, user, product_id):
        product = get_object_or_404(Product, pk=product_id)

        order, created = Order.objects.get_or_create(
            buyer=user,
            product=product,
            is_paid=False,
            defaults={'quantity': 1}
        )
        if not created:
            order.quantity += 1
            order.save()


class OrderImage(models.Model):
    file_path = models.ImageField(upload_to='order_images/')
    image_name = models.CharField(max_length=100)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
