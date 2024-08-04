from django.urls import path
import localfood_app.views as views
from .views import (
    HomePageView,
)


app_name = 'localfood_app'


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),

]