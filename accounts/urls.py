from django.urls import path
from .views import vendor_signup, customer_signup, login_view, logout_view

urlpatterns = [
    path('vendor/signup/', vendor_signup, name='vendor_signup'),
    path('customer/signup/', customer_signup, name='customer_signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
