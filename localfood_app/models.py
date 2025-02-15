from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Attributes:
        is_buyer (bool): Indicates if the user is a buyer.
        is_seller (bool): Indicates if the user is a seller.
    """
    is_buyer = models.BooleanField('buyer status', default=False)
    is_seller = models.BooleanField('seller status', default=False)


class Category(models.Model):
    """
    Model representing a product category.

    Attributes:
        name (str): The name of the category.
        slug (str): The slug (URL-friendly identifier) of the category.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        """
        Returns the string representation of the category, which is its name.

        :return: The name of the category.
        """
        return self.name


class Product(models.Model):
    """
    Model representing a product.

    Attributes:
        name (str): The name of the product.
        description (str): The description of the product.
        price (Decimal): The price of the product.
        quantity (int): The available quantity of the product.
        category (Category): The category to which the product belongs.
        seller (User): The seller of the product.
        created_at (datetime): The date and time when the product was created.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=False, blank=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_primary_image(self):
        """
        Retrieves the primary image associated with the product.

        :return: The first product image associated with the product.
        """
        return self.productimage_set.first()


class ProductImage(models.Model):
    """
    Model representing an image associated with a product.

    Attributes:
        file_path (ImageField): The file path to the product image.
        product (Product): The product to which the image belongs.
    """
    file_path = models.ImageField(upload_to='product_image/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)


class Address(models.Model):
    """
    Model representing a user's address.

    Attributes:
        PROVINCE_CHOICES (tuple): The list of province choices.
        user (User): The user to whom the address belongs.
        city (str): The city of the address.
        street_name (str): The name of the street.
        street_number (str): The number of the street.
        apartment_number (str): The apartment number.
        unit_number (str): The unit number.
        province (str): The province of the address.
        postal_code (str): The postal code of the address.
    """
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
    """
    Model representing an order.

    Attributes:
        buyer (User): The buyer who placed the order.
        created_at (datetime): The date and time when the order was created.
        realization_date (datetime): The date and time when the order was realized.
        is_paid (bool): Indicates if the order has been paid for.
        is_realized (bool): Indicates if the order has been realized.
    """
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    realization_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    is_realized = models.BooleanField(default=False)

    @classmethod
    def add_product_to_basket(cls, user, product_id):
        """
        Adds a product to the user's shopping basket.
        If the product is already in the basket, increments the quantity.

        :param user: The user who is adding the product to the basket.
        :param product_id: The ID of the product to add.
        """
        product = get_object_or_404(Product, pk=product_id)

        order, created = Order.objects.get_or_create(
            buyer=user,
            is_paid=False
        )

        order_product, created = OrderProduct.objects.get_or_create(
            order=order,
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            order_product.quantity += 1
            order_product.save()


class OrderProduct(models.Model):
    """
    Model representing a product within an order.

    Attributes:
        product (Product): The product associated with the order.
        order (Order): The order to which the product belongs.
        quantity (int): The quantity of the product in the order.
        created_at (datetime): The date and time when the order product was created.
    """
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=False, blank=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, blank=False)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total_price(self):
        """
        Calculates the total price of the product based on its quantity and price.

        :return: The total price of the product in the order.
        """
        return self.product.price * self.quantity


class OrderImage(models.Model):
    """
    Model representing an image associated with an order.

    Attributes:
        file_path (ImageField): The file path to the order image.
        order (Order): The order to which the image belongs.
    """
    file_path = models.ImageField(upload_to='order_images/')
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
