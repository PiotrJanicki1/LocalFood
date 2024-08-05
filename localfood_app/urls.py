from django.urls import path
import localfood_app.views as views
from .views import (
    HomePageView,
    CreateUserView,
    LoginView,
)


app_name = 'localfood_app'


urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),

]
