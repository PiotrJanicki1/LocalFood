from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views import View
from .models import Product, User, ProductImage
from .form import UserCreateForm, AddProductForm, LoginForm
from django.contrib.auth.mixins import LoginRequiredMixin


class HomePageView(LoginRequiredMixin, View):
    def get(self, request):
        paginator = Paginator(Product.objects.all().order_by('-created_at'), 10)
        page = request.GET.get('page')
        products = paginator.get_page(page)
        ctx = {
            'products': products
        }
        return render(request, 'localfood_app/base.html', ctx)


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
            return redirect('localfood_app:login')
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
            product = form.save(commit=False)
            product.seller = request.user
            product.save()

            if 'file_path' in request.FILES:
                ProductImage.objects.create(
                    product=product,
                    file_path=request.FILES['file_path'],
                )

            return redirect('localfood_app:ongoing_sale')
        return render(request, 'localfood_app/add_product.html', {'form': form})


class OngoingSaleView(View):
    def get(self, request):
        paginator = Paginator(Product.objects.filter(seller=request.user).order_by('created_at'), 10)
        page = request.GET.get('page')
        products = paginator.get_page(page)
        return render(request, 'localfood_app/ongoing_sale.html', {'products': products})






