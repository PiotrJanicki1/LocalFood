from django.urls import path
from .views import (
    HomePageView,
    CreateUserView,
    LoginView,
    AddProductView,
    OngoingSaleView,
    CategoryProductView,
    BasketView,
    EditBasketView,
    OrderHistoryView,
    OrderHistoryDetailView,
    ProductDetailView,
    SellerOrderView,
    SellerOrderDetailView
)


app_name = 'localfood_app'


urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'),
    # path('sales/', SalesPageView.as_view(), name='sales'),
    path('add_product/', AddProductView.as_view(), name='add_product'),
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('ongoing_sale/', OngoingSaleView.as_view(), name='ongoing_sale'),
    path('category/<slug:slug>/', CategoryProductView.as_view(), name='category'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('basket/edit/<int:order_product_id>/', EditBasketView.as_view(), name='edit_basket'),
    path('order_history/', OrderHistoryView.as_view(), name='order_history'),
    path('order_history/<int:order_id>/', OrderHistoryDetailView.as_view(), name='order_history_detail'),
    path('product_detail/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('seller_orders/', SellerOrderView.as_view(), name='seller_order'),
    path('seller_order_detail/<int:order_id>/', SellerOrderDetailView.as_view(), name='seller_order_detail'),

]
