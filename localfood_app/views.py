from django.shortcuts import render, redirect
from django.views import View
from .models import Category, Product, User
from .form import UserCreateForm


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
