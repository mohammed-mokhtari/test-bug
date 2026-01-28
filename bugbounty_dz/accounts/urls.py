from django.urls import path
from .views import Home, HackerLoginView, HackerRegisterView
from .views import HackerHomeView, HackerLogoutView,enterprise_register, enterprise_login

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('hacker/login/', HackerLoginView.as_view(), name='hacker_login'),
    path('hacker/register/', HackerRegisterView.as_view(), name='hacker_register'),
    path('hacker/home/', HackerHomeView.as_view(), name='hacker_home'),
    path('hacker/logout/', HackerLogoutView.as_view(), name='hacker_logout'),
    path('enterprise/register/', enterprise_register, name='enterprise_register'),
    path("enterprise/login/", enterprise_login, name="enterprise_login"),
]
