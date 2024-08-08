from django.urls import path
import localfood_app.views as views
from .views import (
    HomePageView,
    CreateUserView,
    LoginView,
    SalesPageView,
    AddProductView,
)


app_name = 'localfood_app'


urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'),
    path('sales/', SalesPageView.as_view(), name='sales'),
    path('add_product/', AddProductView.as_view(), name='add_product'),
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
]