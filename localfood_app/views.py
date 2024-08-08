from django.shortcuts import render, redirect
from django.views import View
from .models import Product, User
from .form import UserCreateForm, AddProductForm
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


class SalesPageView(View):
    def get(self, request):
        return render(request, 'localfood_app/sales_page.html')


class AddProductView(View):
    def get(self, request):
        form = AddProductForm()
        return render(request, 'localfood_app/add_product.html', {'form': form})

    # def post(self, request):
    #     product_form = ProductForm(request.POST)
    #     image_form = ProductImageForm(request.POST, request.FILES)
    #
    #     if product_form.is_valid() and image_form.is_valid():
    #         product = product_form.save(commit=False)
    #         product.seller = request.user  # Przypisz zalogowanego użytkownika jako sprzedawcę
    #         product.save()
    #
    #         image = image_form.save(commit=False)
    #         image.product = product
    #         image.save()
    #
    #         return redirect('product_list')  # Upewnij się, że masz odpowiednią nazwę URL
    #     return render(request, 'localfood_app/add_product.html',
    #                   {'product_form': product_form, 'image_form': image_form})

    def post(self, request):
        form = AddProductForm(request.POST, request.FILES)  # Dodaj request.FILES

        if form.is_valid():
            form.save()
            return redirect('/sales/')

        return render(request, 'localfood_app/add_product.html', {'form': form})






