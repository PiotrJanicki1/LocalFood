from django.shortcuts import render
from django.views import View
from .models import Category, Product

class HomePageView(View):
    def get(self, request):
        categories = Category.objects.all()
        products = Product.objects.order_by('-created_at')

        ctx = {
            'categories': categories,
            'products': products
        }

        return render(request, 'base.html', ctx)


