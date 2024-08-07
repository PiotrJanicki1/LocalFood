from typing import Any
from .models import Product, ProductImage, Category

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

class AddProductForm(forms.Form):
   name = forms.CharField(max_length=100)
   description = forms.CharField(widget=forms.Textarea)
   price = forms.DecimalField(max_digits=5, decimal_places=2)
   quantity = forms.IntegerField(min_value=1)
   category = forms.ModelChoiceField(queryset=Category.objects.all())
   file_path = forms.FilePathField
   image_name = forms.CharField(widget=forms.Textarea)
