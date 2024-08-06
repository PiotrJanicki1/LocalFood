from django.urls import path
import localfood_app.views as views
from .views import (
    HomePageView,
    SalesPageView
)


app_name = 'localfood_app'


urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'),
    path('sales/', SalesPageView.as_view(), name='sales'),
]