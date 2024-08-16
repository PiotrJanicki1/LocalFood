from audioop import reverse

from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Product, User, ProductImage, Order, OrderProduct
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
        return render(request, 'localfood_app/dashboard.html', ctx)

    def post(self, request):
        product_id = request.POST.get('product_id')
        Order.add_product_to_basket(request.user, product_id)

        return redirect(request.META.get('HTTP_REFERER'))




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
        paginator = Paginator(Product.objects.filter(seller=request.user).order_by('-created_at'), 10)
        page = request.GET.get('page')
        products = paginator.get_page(page)
        return render(request, 'localfood_app/ongoing_sale.html', {'products': products})


class CategoryProductView(View):
    def get(self, request, slug):
        paginator = Paginator(Product.objects.filter(category__slug=slug).order_by('-created_at'), 10)
        page = request.GET.get('page')
        products = paginator.get_page(page)
        return render(request, 'localfood_app/dashboard.html', {'products': products})

    def post(self, request, slug):
        product_id = request.POST.get('product_id')
        Order.add_product_to_basket(request.user, product_id)

        return redirect(request.META.get('HTTP_REFERER'))



class BasketView(View):
    def get(self, request):
        buyer = request.user

        try:
            order = Order.objects.get(is_paid=False, buyer=buyer)
        except Order.DoesNotExist:
            return render(request, 'localfood_app/basket_empty.html')


        if order:
            order_products = OrderProduct.objects.filter(order=order)
            paginator = Paginator(order_products.order_by('-created_at'), 20)
            page = request.GET.get('page')
            order_products = paginator.get_page(page)
            total_price = sum(order_product.calculate_total_price() for order_product in order_products)

            ctx = {
                'order_products': order_products,
                'total_price': total_price,
                'order': order
            }
            print(f"Order_id: {order.id}")
            return render(request, 'localfood_app/basket.html', ctx)


    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'post':
            return self.payment(request)
        return super().dispatch(request, *args, **kwargs)


    def payment(self, request):
        order_id = request.POST.get('order_id')
        payment_value = request.POST.get('payment')

        if payment_value == 'paid' and order_id:
            try:
                order = Order.objects.get(id=order_id, buyer=request.user)
                if not order.is_paid:
                    order.is_paid = True
                    order.save()
                return redirect('localfood_app:home')
            except Order.DoesNotExist:
                return redirect('localfood_app:basket')

        return redirect('localfood_app:basket')


class EditBasketView(View):
    def get(self, request, order_product_id):
        product = get_object_or_404(OrderProduct, id=order_product_id)
        return render(request, 'localfood_app/edit_basket.html', {'product': product})

    def post(self, request, order_product_id):
        product = OrderProduct.objects.get(id=order_product_id)
        new_quantity = request.POST.get('quantity')

        if new_quantity and new_quantity.isdigit():
            new_quantity = int(new_quantity)
            if new_quantity > 0:
                product.quantity = new_quantity
                product.save()

                return redirect('localfood_app:basket')

            return HttpResponse("Invalid quantity or method", status=400)

        elif request.POST.get('_method') == 'delete':
             product = OrderProduct.objects.get(id=order_product_id)
             product.delete()

             return redirect('localfood_app:basket')

        return HttpResponse("Invalid request method or parameters", status=400)


    # def delete(self, request, order_product_id):
    #     if request.POST.get('_method') == 'delete':
    #         product = OrderProduct.objects.get(id=order_product_id)
    #         product.delete()
    #         return redirect('localfood_app:basket')
    #
    #     return HttpResponse("Invalid request method or parameters", status=400)


class OrderHistoryView(View):
    def get(self, request):
        paginator = Paginator(Order.objects.filter(is_paid=True).order_by('-created_at'), 10)
        page = request.GET.get('page')
        orders = paginator.get_page(page)
        ctx = {
            'orders': orders
        }

        return render(request, 'localfood_app/order_history.html', ctx)


class OrderHistoryDetailView(View):
    def get(self, request, order_id):
        paginator = Paginator(OrderProduct.objects.filter(order_id=order_id), 10)
        page = request.GET.get('page')
        order_products = paginator.get_page(page)
        total_price = sum(order_product.calculate_total_price() for order_product in order_products)
        ctx = {
            'order_products': order_products,
            'total_price': total_price,
        }

        return render(request, 'localfood_app/history_detail.html', ctx)



















