from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls.base import reverse_lazy
from django.views import View
from django.views.generic.edit import UpdateView

from .models import Product, User, ProductImage, Order, OrderProduct
from .form import UserCreateForm, AddProductForm, LoginForm, ProfileForm
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
    View for handling user
    istration.
    """
    def get(self, request):
        """
       Handles GET requests to display the user registration form.

       :param request: The HTTP request object.
       :return: Rendered signup page with the registration form.
       """
        form = UserCreateForm()
        return render(request, 'localfood_app/signup.html', {'form': form})

    def post(self, request):
        """
        Handles POST requests to create a new user account.

        :param request: The HTTP request object.
        :return: Redirects to the login page if successful,
         otherwise re-renders the signup page with errors.
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
        :return: Redirects to the home page if successful,
         otherwise re-renders the login page with errors.
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
        :return: Redirects to the ongoing sales page if successful,
         otherwise re-renders the add product page with errors.
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
            print(f"Product saved: {product}")
            return redirect('localfood_app:ongoing_sale')
        else:
            print(f"Form errors: {form.errors}")
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
        paginator = Paginator(Product.objects.filter(seller=request.user).
                              order_by('-created_at'), 10)
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
        paginator = Paginator(Product.objects.filter(category__slug=slug).
                              order_by('-created_at'), 10)
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
        :return: Rendered basket page with order products and total price,
         or an empty basket page if no items.
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
            total_price = sum(order_product.calculate_total_price()
                              for order_product in order_products)

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
        :return: Redirects to the home page if payment is successful,
         otherwise redirects to the basket page.
        """
        order_id = request.POST.get('order_id')
        payment_value = request.POST.get('payment')

        if not order_id or not payment_value:
            return HttpResponseBadRequest("Order ID and payment value are required.")

        if not order_id.isdigit():
            return HttpResponseBadRequest("Invalid order ID format.")

        order_id = int(order_id)

        if payment_value != 'paid':
            return HttpResponseBadRequest("Invalid payment value.")

        try:
            order = Order.objects.get(id=order_id, buyer=request.user)
            if not order.is_paid:
                order.is_paid = True
                order.save()
            return redirect('localfood_app:home')
        except Order.DoesNotExist:
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
        paginator = Paginator(Order.objects.filter(is_paid=True, buyer = request.user).order_by('-created_at'), 10)
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
        paginator = Paginator(OrderProduct.objects.filter(order_id=order_id, order__buyer = request.user), 10)
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

        paginator = Paginator(OrderProduct.objects.filter(product__seller=seller), 10)
        page = request.GET.get('page')
        order_products = paginator.get_page(page)
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
        paginator = Paginator(OrderProduct.objects.filter(order_id=order_id, product__seller=request.user), 10)
        page = request.GET.get('page')
        order_products = paginator.get_page(page)
        total_price = sum(order_product.calculate_total_price() for order_product in order_products)
        ctx = {
            'order_products': order_products,
            'total_price': total_price,
        }

        return render(request, 'localfood_app/seller_order_detail.html', ctx)

class ProductSearchView(View):
    """
    View for handling product search functionality.
    """
    def get(self, request):
        """
        Handles GET requests to search for products based on user input.

        :param request: The HTTP request object containing the search query.
        :return: Rendered search results page with filtered products and pagination.
        """
        query = request.GET.get('q', '').strip()

        if query:
            queryset = Product.objects.filter(name__icontains=query)

        else:
            queryset = Product.objects.all()

        paginator = Paginator(queryset, 10)
        page = request.GET.get('page')
        products = paginator.get_page(page)

        ctx = {
            'products': products,
            'query': query,
        }

        return render(request, 'localfood_app/search.html', ctx)

class ProfileView(View):
    """
    View for displaying and editing the user's profile.
    """
    def get(self, request):
        """
        Handles GET requests to display the user's profile page.

        :param request: The HTTP request object.
        :return: Rendered profile page with user details.
        """
        return render(request, 'localfood_app/profile.html', {'user': request.user})

    def profile_edit(self, request):
        """
        Handles POST requests for updating user profile information.

        :param request: The HTTP request object containing updated profile data.
        :return: Redirects to the profile page upon successful update.
        """
        if request.method == 'POST':
            form = ProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('localfood_app:profile')

        else:
            form = ProfileForm(instance=request.user)

        return render(request, 'localfood_app/profile_edit.html', {'form': form})

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating user profile details.
    """
    model = User
    form_class = ProfileForm
    template_name = 'localfood_app/profile_edit.html'
    success_url = reverse_lazy('localfood_app:profile')

    def get_object(self):
        """
        Returns the current user instance to be updated.

        :return: The logged-in user instance.
        """
        return self.request.user


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    View for allowing users to change their passwords.
    """
    template_name = 'localfood_app/change_password.html'
    success_url = reverse_lazy('localfood_app:profile')
    form_class = PasswordChangeForm

    def form_valid(self, form):
        """
        Handles successful password change and updates the session.

        :param form: The password change form submitted by the user.
        :return: Redirects to the profile page upon successful password update.
        """
        user = form.save()
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)


class LogoutView(View):
    """
    View for handling user logout functionality.
    """

    def get(self, request):
        """
        Handles GET requests to log the user out and redirect to home.

        :param request: The HTTP request object.
        :return: Redirects to the home page after logging out.
        """
        logout(request)
        return redirect('localfood_app:home')
