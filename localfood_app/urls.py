from django.urls import path
import localfood_app.views as views
from .views import (
    HomePageView,
    CreateUserView,
    LoginView,
    SalesPageView,
    AddProductView,
    OngoingSaleView,
    CategoryProductView,
    BasketView,
)


app_name = 'localfood_app'


urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'),
    path('sales/', SalesPageView.as_view(), name='sales'),
    path('add_product/', AddProductView.as_view(), name='add_product'),
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('ongoing_sale/', OngoingSaleView.as_view(), name='ongoing_sale'),
    path('category/<slug:slug>/', CategoryProductView.as_view(), name='category'),
    path('basket/', BasketView.as_view(), name='basket'),

]