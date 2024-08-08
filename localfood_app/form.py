from typing import Any

import django.forms as forms
from django.core.exceptions import ValidationError
from .validators import validate_username_unique


class UserCreateForm(forms.Form):
    ACCOUNT_CHOICES = [
        ('business', 'Business Account'),
        ('consumer', 'Consumer Account'),
    ]

    username = forms.CharField(validators=[validate_username_unique])
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    account_type = forms.ChoiceField(choices=ACCOUNT_CHOICES)

    def clean(self) -> dict[str, Any]:
        data = super().clean()
        if data['password1'] != data['password2']:
            raise ValidationError('Passwords must match')
        return data


# class LoginForm(forms.Form):
#     username = forms.CharField()
#     password = forms.CharField(widget=forms.PasswordInput)
