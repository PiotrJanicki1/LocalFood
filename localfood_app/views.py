from audioop import reverse

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from .models import Category, Product, User
from .form import UserCreateForm, LoginForm


class HomePageView(View):
    def get(self, request):
        categories = Category.objects.all()
        products = Product.objects.order_by('-created_at')

        ctx = {
            'categories': categories,
            'products': products
        }

        return render(request, 'localfood_app/base.html', ctx)


class CreateUserView(View):
    def get(self, request):
        form = UserCreateForm()
        return render(request, 'localfood_app/signup.html', {'form': form})

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            account_type = form.cleaned_data['account_type']
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )

            if account_type == 'business':
                user.is_seller = True

            elif account_type == 'consumer':
                user.is_buyer = True

            user.save()
            return redirect('localfood_app:login')
        else:
            return render(request, 'localfood_app/signup.html', {'form': form})


# class LoginView(View):
#     def get(self, request):
#         form = LoginForm()
#         return render(request, 'localfood_app/login.html', {'form': form})
#
#     def post(self, request):
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             user = authenticate(
#                 username=form.cleaned_data['username'],
#                 password=form.cleaned_data['password'],
#             )
#             if user:
#                 login(request, user)
#                 return redirect("localfood_app:home")
#
#         return render(request, 'localfood_app/login.html', {'form': form})
