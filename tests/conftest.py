import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'password1': 'password123',
        'password2': 'password123',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'testuser@example.com',
        'account_type': 'consumer'
    }

@pytest.fixture
def user(client, user_data):
    user = User.objects.create_user(
        username=user_data['username'],
        password=user_data['password1'],
        email=user_data['email'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name']
    )
    client.login(username=user_data['username'], password=user_data['password1'])
    return user

@pytest.fixture
def image_upload():
    image = BytesIO()
    img = Image.new('RGB', (100, 100), color='red')
    img.save(image, format='JPEG')
    image.seek(0)
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=image.read(),
        content_type='image/jpeg'
    )