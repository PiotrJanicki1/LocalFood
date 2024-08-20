from typing import Any
from .models import Product
import django.forms as forms
from django.core.exceptions import ValidationError
from .validators import validate_username_unique


class UserCreateForm(forms.Form):
    """
    Form for creating a new user account.

    Attributes:
        ACCOUNT_CHOICES (list): Choices for the account type (business or consumer).
        username (CharField): The username for the new account.
        password1 (CharField): The password for the new account.
        password2 (CharField): The repeated password for confirmation.
        first_name (CharField): The first name of the user.
        last_name (CharField): The last name of the user.
        email (EmailField): The email address of the user.
        account_type (ChoiceField): The type of account being created.
    """
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
        """
        Validate that the two entered passwords match.

        Returns:
            dict: The cleaned data.

        Raises:
            ValidationError: If the two passwords do not match.
        """
        data = super().clean()
        if data['password1'] != data['password2']:
            raise ValidationError('Passwords must match')
        return data


class LoginForm(forms.Form):
    """
    Form for logging in a user.

    Attributes:
        username (CharField): The username of the user.
        password (CharField): The password for the user account.
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)



class AddProductForm(forms.ModelForm):
    """
    Form for adding a new product.

    Attributes:
        file_path (ImageField): The image associated with the product.
        name (CharField): The name of the product.
        description (TextField): The description of the product.
        price (DecimalField): The price of the product.
        quantity (PositiveIntegerField): The available quantity of the product.
        category (ForeignKey): The category to which the product belongs.
    """
    file_path = forms.ImageField(required=True)

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'quantity', 'category', 'file_path']
