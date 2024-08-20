from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Product, User, ProductImage, Order, OrderProduct
from .form import UserCreateForm, AddProductForm, LoginForm
from django.contrib.auth.mixins import LoginRequiredMixin


class HomePageView(LoginRequiredMixin, View):
    """
    View for displaying the home page with a list of products.
    """
    def get(self, request):
        """
        Handles GET requests to display the home page with a paginated list of products.

        :param request: The HTTP request object.
        :return: Rendered home page with a list of products.
        """
        paginator = Paginator(Product.objects.all().order_by('-created_at'), 10)
        page = request.GET.get('page')
        products = paginator.get_page(page)
        ctx = {
            'products': products
        }
        return render(request, 'localfood_app/dashboard.html', ctx)

    def post(self, request):
        """
        Handles POST requests to add a product to the basket.

        :param request: The HTTP request object.
        :return: Redirect back to the previous page.
       """
        product_id = request.POST.get('product_id')
        Order.add_product_to_basket(request.user, product_id)

        return redirect(request.META.get('HTTP_REFERER'))


class CreateUserView(View):
    """
    View for handling user registration.
    """
    def get(self, request):
        """
       Handles GET requests to display the user registration form.

       :param request: The HTTP request object.
       :return: Rendered signup page with the registration form.
       """
        form = UserCreateForm
        return render(request, 'localfood_app/signup.html', {'form': form})

    def post(self, request):
        """
        Handles POST requests to create a new user account.

        :param request: The HTTP request object.
        :return: Redirects to the login page if successful, otherwise re-renders the signup page with errors.
        """
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
    """
    View for handling user login.
    """
    def get(self, request):
        """
        Handles GET requests to display the login form.

        :param request: The HTTP request object.
        :return: Rendered login page with the login form.
        """
        form = LoginForm()
        return render(request, 'localfood_app/login.html', {'form': form})

    def post(self, request):
        """
        Handles POST requests to authenticate and log in a user.

        :param request: The HTTP request object.
        :return: Redirects to the home page if successful, otherwise re-renders the login page with errors.
        """
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


class AddProductView(View):
    """
    View for adding a new product.
    """
    def get(self, request):
        """
        Handles GET requests to display the product creation form.

        :param request: The HTTP request object.
        :return: Rendered add product page with the product form.
        """
        form = AddProductForm()
        return render(request, 'localfood_app/add_product.html', {'form': form})


    def post(self, request):
        """
        Handles POST requests to create a new product.

        :param request: The HTTP request object.
        :return: Redirects to the ongoing sales page if successful, otherwise re-renders the add product page with errors.
        """
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
    """
    View for displaying a seller's ongoing sales.
    """
    def get(self, request):
        """
        Handles GET requests to display a list of the seller's ongoing sales.

        :param request: The HTTP request object.
        :return: Rendered ongoing sales page with a list of products.
        """
        paginator = Paginator(Product.objects.filter(seller=request.user).order_by('-created_at'), 10)
        page = request.GET.get('page')
        products = paginator.get_page(page)
        return render(request, 'localfood_app/ongoing_sale.html', {'products': products})


class CategoryProductView(View):
    """
   View for displaying products in a specific category.
   """
    def get(self, request, slug):
        """
        Handles GET requests to display products filtered by category.

        :param request: The HTTP request object.
        :param slug: The slug of the category.
        :return: Rendered category products page with a list of products.
        """
        paginator = Paginator(Product.objects.filter(category__slug=slug).order_by('-created_at'), 10)
        page = request.GET.get('page')
        products = paginator.get_page(page)
        return render(request, 'localfood_app/dashboard.html', {'products': products})

    def post(self, request, slug):
        """
        Handles POST requests to add a product from a specific category to the basket.

        :param request: The HTTP request object.
        :param slug: The slug of the category.
        :return: Redirects back to the previous page.
        """
        product_id = request.POST.get('product_id')
        Order.add_product_to_basket(request.user, product_id)

        return redirect(request.META.get('HTTP_REFERER'))


class BasketView(View):
    """
    View for displaying the user's shopping basket.
    """
    def get(self, request):
        """
        Handles GET requests to display the user's current shopping basket.

        :param request: The HTTP request object.
        :return: Rendered basket page with order products and total price, or an empty basket page if no items.
        """
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
            return render(request, 'localfood_app/basket.html', ctx)


    def dispatch(self, request, *args, **kwargs):
        """
        Custom dispatch method to handle payment logic on POST requests.

        :param request: The HTTP request object.
        :return: Calls payment method on POST, or default dispatch on other requests.
        """
        if request.method.lower() == 'post':
            return self.payment(request)
        return super().dispatch(request, *args, **kwargs)


    def payment(self, request):
        """
        Handles payment processing for an order.

        :param request: The HTTP request object.
        :return: Redirects to the home page if payment is successful, otherwise redirects to the basket page.
        """
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
    """
    View for editing items in the shopping basket.
    """
    def get(self, request, order_product_id):
        """
        Handles GET requests to display the edit page for a specific basket item.

        :param request: The HTTP request object.
        :param order_product_id: The ID of the order product to edit.
        :return: Rendered edit basket page with the selected product.
        """
        product = get_object_or_404(OrderProduct, id=order_product_id)
        return render(request, 'localfood_app/edit_basket.html', {'product': product})

    def post(self, request, order_product_id):
        """
        Handles POST requests to update the quantity or delete an item in the basket.

        :param request: The HTTP request object.
        :param order_product_id: The ID of the order product to update or delete.
        :return: Redirects to the basket page after the update or delete operation.
        """
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
    """
    View for displaying the user's order history.
    """
    def get(self, request):
        """
        Handles GET requests to display a paginated list of the user's history paid orders.

        :param request: The HTTP request object.
        :return: Rendered order history page with a list of orders.
        """
        paginator = Paginator(Order.objects.filter(is_paid=True).order_by('-created_at'), 10)
        page = request.GET.get('page')
        orders = paginator.get_page(page)
        ctx = {
            'orders': orders
        }

        return render(request, 'localfood_app/order_history.html', ctx)


class OrderHistoryDetailView(View):
    """
    View for displaying the details of a specific order in the user's order history.
    """
    def get(self, request, order_id):
        """
        Handles GET requests to display the details of a specific order.

        :param request: The HTTP request object.
        :param order_id: The ID of the order to display details for.
        :return: Rendered order detail page with the order products and total price.
        """
        paginator = Paginator(OrderProduct.objects.filter(order_id=order_id), 10)
        page = request.GET.get('page')
        order_products = paginator.get_page(page)
        total_price = sum(order_product.calculate_total_price() for order_product in order_products)
        ctx = {
            'order_products': order_products,
            'total_price': total_price,
        }

        return render(request, 'localfood_app/history_detail.html', ctx)


class ProductDetailView(View):
    """
    View for displaying the details of a specific product.
    """
    def get(self, request, product_id):
        """
        Handles GET requests to display the details of a specific product.

        :param request: The HTTP request object.
        :param product_id: The ID of the product to display.
        :return: Rendered product detail page.
        """
        product = Product.objects.get(id=product_id)
        return render(request, 'localfood_app/product_detail.html', {'product': product})

    def post(self, request, product_id):
        """
        Handles POST requests to add the product to the user's basket.

        :param request: The HTTP request object.
        :param product_id: The ID of the product to add to the basket.
        :return: Redirects to the home page.
        """
        Order.add_product_to_basket(request.user, product_id)

        return redirect('localfood_app:home')


class SellerOrderView(View):
    """
    View for displaying orders for a specific seller.
    """
    def get(self, request):
        """
        Handles GET requests to display a list of orders for the seller's products.

        :param request: The HTTP request object.
        :return: Rendered seller orders page with a list of orders.
        """
        seller = request.user

        order_products = OrderProduct.objects.filter(product__seller=seller)
        orders = Order.objects.filter(orderproduct__in=order_products).distinct()

        ctx = {
            'order_products': order_products,
            'orders': orders
        }
        return render(request, 'localfood_app/seller_orders.html', ctx)


class SellerOrderDetailView(View):
    """
    View for displaying the details of a specific order for a seller.
    """
    def get(self, request, order_id):
        """
        Handles GET requests to display the details of a specific order for a seller.

        :param request: The HTTP request object.
        :param order_id: The ID of the order to display details for.
        :return: Rendered seller order detail page with the order products and total price.
        """
        paginator = Paginator(OrderProduct.objects.filter(order_id=order_id), 10)
        page = request.GET.get('page')
        order_products = paginator.get_page(page)
        total_price = sum(order_product.calculate_total_price() for order_product in order_products)
        ctx = {
            'order_products': order_products,
            'total_price': total_price,
        }

        return render(request, 'localfood_app/seller_order_detail.html', ctx)
