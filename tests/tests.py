from io import BytesIO
from unittest.mock import patch
import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from localfood_app.form import UserCreateForm, AddProductForm
from localfood_app.models import Category, Product, Order, OrderProduct
from conftest import client, user_data, user, User, image_upload



@pytest.mark.django_db
def test_signup_view_get(client):
    """
    Test GET request for signup view to ensure the registration form is rendered.
    """
    response = client.get(reverse('localfood_app:signup'))
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, UserCreateForm)


@pytest.mark.django_db
def test_signup_view_post_valid(client, user_data):
    """
    Test POST request for signup view with valid data to ensure user is created
    and redirected to login page.
    """
    response = client.post(reverse('localfood_app:signup'), data=user_data)
    assert response.status_code == 302
    assert User.objects.filter(username=user_data['username']).exists()


@pytest.mark.django_db
def test_signup_view_post_invalid(client, user_data):
    """
    Test POST request for signup view with invalid data to ensure form errors are displayed.
    """
    user_data['password2'] = 'differentpassword'
    response = client.post(reverse('localfood_app:signup'), data=user_data)
    assert response.status_code == 200
    assert 'form' in response.context
    form = response.context['form']

    print("Form errors:", form.errors)

    assert not form.is_valid()
    assert 'Passwords must match' in form.errors.get('password2', [])


@pytest.mark.django_db
def test_login_view_post_valid(client, user_data):
    """
    Test POST request for login view with valid credentials.
    """
    User.objects.create_user(
        username=user_data['username'],
        password=user_data['password1'],
        email=user_data['email'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name']
    )
    response = client.post(reverse('localfood_app:login'), {
        'username': user_data['username'],
        'password': user_data['password1'],
    })
    assert response.status_code == 302
    assert response.url == reverse('localfood_app:home')


@pytest.mark.django_db
def test_login_view_post_invalid(client):
    """
    Test POST request for login view with invalid credentials.
    """
    response = client.post(reverse('localfood_app:login'), {
        'username': 'wronguser',
        'password': 'wrongpassword',
    })
    assert response.status_code == 200

    print(response.content.decode())

    assert 'Please enter a correct username and password.' in response.content.decode()


@pytest.mark.django_db
def test_add_product_view_get(client, user):
    """
    Test GET request for add product view to ensure the form is rendered.
    """
    response = client.get(reverse('localfood_app:add_product'))
    assert response.status_code == 200
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, AddProductForm)


@pytest.mark.django_db
def test_add_product_view_post_valid(client, user, image_upload):
    """
    Test POST request for add product view with valid data to ensure product is added
    and redirected to ongoing sale page.
    """
    category = Category.objects.create(name='Test Category', slug='test-category')

    with patch('django.core.files.storage.default_storage.save') as mock_save:
        mock_save.return_value = 'mock_path/test_image.jpg'

        image = BytesIO()
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image, format='JPEG')
        image.seek(0)

        uploaded_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=image.read(),
            content_type='image/jpeg'
        )

        response = client.post(reverse('localfood_app:add_product'), {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': 10.00,
            'quantity': 5,
            'category': category.id,
            'file_path': image_upload
        })

        assert response.status_code == 302
        assert Product.objects.filter(name='Test Product').exists()
        mock_save.assert_called_once()


@pytest.mark.django_db
def test_basket_view_get(client, user):
    """
    Test GET request for basket view to ensure basket is displayed correctly.
    """
    category = Category.objects.create(name='Test Category', slug='test-category')
    product = Product.objects.create(
        name='Test Product',
        description='Test Description',
        price=10.00,
        quantity=5,
        category=category,
        seller=user
    )
    order = Order.objects.create(buyer=user)
    OrderProduct.objects.create(order=order, product=product, quantity=1)

    response = client.get(reverse('localfood_app:basket'))

    print("Response content:", response.content.decode())
    print("Response context:", response.context)

    assert response.status_code == 200

    assert 'order_products' in response.context
    order_products = response.context['order_products']

    assert len(order_products) > 0
    assert order_products[0].product.name == 'Test Product'
    assert response.context['total_price'] == product.price


@pytest.mark.django_db
def test_basket_view_payment_valid(client, user):
    """
    Test POST request for basket view with valid payment to ensure order is marked as paid
    and redirected to home page.
    """
    category = Category.objects.create(name='Test Category', slug='test-category')
    product = Product.objects.create(
        name='Test Product',
        description='Test Description',
        price=10.00,
        quantity=5,
        category=category,
        seller=user
    )
    Order.add_product_to_basket(user, product.id)
    order = Order.objects.get(buyer=user, is_paid=False)

    response = client.post(reverse('localfood_app:basket'), {
        'order_id': order.id,
        'payment': 'paid'
    })
    assert response.status_code == 302
    order.refresh_from_db()
    assert order.is_paid


@pytest.mark.django_db
def test_basket_view_payment_invalid(client, user):
    """
    Test POST request for basket view with invalid payment to ensure proper redirection
    or error handling.
    """
    category = Category.objects.create(name='Test Category', slug='test-category')
    product = Product.objects.create(
        name='Test Product',
        description='Test Description',
        price=10.00,
        quantity=5,
        category=category,
        seller=user
    )

    Order.add_product_to_basket(user, product.id)

    response = client.post(reverse('localfood_app:basket'), {
        'order_id': 'invalid_id',
        'payment': 'paid'
    })

    assert response.status_code == 400

    response = client.post(reverse('localfood_app:basket'), {
        'order_id': '1',
        'payment': 'invalid_value'
    })

    assert response.status_code == 400


@pytest.mark.django_db
def test_product_detail_view_get(client, user):
    """
    Test GET request for product detail view to ensure product details are displayed.
    """
    category = Category.objects.create(name='Test Category', slug='test-category')
    product = Product.objects.create(
        name='Test Product',
        description='Test Description',
        price=10.00,
        quantity=5,
        category=category,
        seller=user
    )
    response = client.get(reverse('localfood_app:product_detail', args=[product.id]))
    assert response.status_code == 200
    assert 'product' in response.context
    assert response.context['product'].name == 'Test Product'


@pytest.mark.django_db
def test_edit_basket_view_get(client, user):
    """
    Test GET request for edit basket view to ensure the basket item is displayed for editing.
    """
    category = Category.objects.create(name='Test Category', slug='test-category')
    product = Product.objects.create(
        name='Test Product',
        description='Test Description',
        price=10.00,
        quantity=5,
        category=category,
        seller=user
    )
    order = Order.objects.create(buyer=user)
    order_product = OrderProduct.objects.create(
        order=order,
        product=product,
        quantity=1
    )
    response = client.get(reverse('localfood_app:edit_basket', args=[order_product.id]))
    assert response.status_code == 200
    assert 'product' in response.context
    assert response.context['product'] == order_product


@pytest.mark.django_db
def test_seller_order_view(client):
    """
    Test GET request for seller order view to ensure orders are displayed correctly.
    """

    category = Category.objects.create(name='Test Category', slug='test-category')

    seller = User.objects.create_user(username='testseller', password='testpassword')
    buyer = User.objects.create_user(username='testbuyer', password='testpassword')

    product1 = Product.objects.create(
        name='Test Product 1',
        description='Test Description 1',
        price=10.00,
        quantity=5,
        category=category,
        seller=seller
    )
    product2 = Product.objects.create(
        name='Test Product 2',
        description='Test Description 2',
        price=15.00,
        quantity=10,
        category=category,
        seller=seller
    )

    order1 = Order.objects.create(buyer=buyer)
    order2 = Order.objects.create(buyer=buyer)

    OrderProduct.objects.create(order=order1, product=product1, quantity=1)
    OrderProduct.objects.create(order=order1, product=product2, quantity=2)
    OrderProduct.objects.create(order=order2, product=product1, quantity=3)

    client.force_login(seller)

    response = client.get(reverse('localfood_app:seller_order'))

    assert response.status_code == 200
    assert 'orders' in response.context
    orders = response.context['orders']

    assert len(orders) == 2
    assert order1 in orders
    assert order2 in orders
    assert product1 in [op.product for op in order1.orderproduct_set.all()]
    assert product2 in [op.product for op in order1.orderproduct_set.all()]


@pytest.mark.django_db
def test_seller_order_detail_view(client, user):
    """
    Test GET request for seller order detail view to ensure detailed order information is displayed.
    """
    category = Category.objects.create(name='Test Category', slug='test-category')
    product = Product.objects.create(
        name='Test Product',
        description='Test Description',
        price=10.00,
        quantity=5,
        category=category,
        seller=user
    )
    order = Order.objects.create(buyer=user)
    order_product = OrderProduct.objects.create(order=order, product=product, quantity=1)

    url = reverse('localfood_app:seller_order_detail', args=[order.id])
    response = client.get(url)

    assert response.status_code == 200
    assert 'order_products' in response.context
    assert list(response.context['order_products']) == [order_product]
    assert response.context['total_price'] == order_product.calculate_total_price()
