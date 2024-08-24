from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


def validate_username_unique(value):
    if User.objects.filter(username=value):
        raise ValidationError('Taka nazwa użytkownika jest już w użyciu')
