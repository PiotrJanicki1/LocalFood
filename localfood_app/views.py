from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from .models import Product, User
from .form import UserCreateForm, AddProductForm, LoginForm
from django.contrib.auth.mixins import LoginRequiredMixin


class HomePageView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        products = Product.objects.order_by('-created_at')
        ctx = {
            'products': products
        }

        if user.is_buyer:
            template_name = 'localfood_app/dashboard_consumer.html'
        elif user.is_seller:
            template_name = 'localfood_app/dashboard_business.html'

        return render(request, template_name, ctx)


class CreateUserView(View):
    def get(self, request):
        form = UserCreateForm
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
            return redirect('login')
        else:
            return render(request, 'localfood_app/signup.html', {'form': form})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'localfood_app/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return redirect("localfood_app:home")

        return render(request, 'localfood_app/login.html', {'form': form})


class SalesPageView(View):
    def get(self, request):
        return render(request, 'localfood_app/sales_page.html')


class AddProductView(View):
    def get(self, request):
        form = AddProductForm()
        return render(request, 'localfood_app/add_product.html', {'form': form})


    def post(self, request):
        form = AddProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('localfood_app:sales')

        return render(request, 'localfood_app/add_product.html', {'form': form})






