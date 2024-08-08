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


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)



class AddProductForm(forms.ModelForm):
    file_path = forms.ImageField(required=True)

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'quantity', 'category', 'file_path']


    def save(self, commit=True):
        product = super().save(commit=False)
        if commit:
            product.save()

        if 'file_path' in self.files:
            ProductImage.objects.create(
                product=product,
                file_path=self.files['file_path'],
            )

        return product



