"""
URL configuration for restro_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Admin route
    path('admin/', admin.site.urls),

    # User-related routes
    path('add-user/', views.add_user, name='add_user'),
    path('users/', views.get_users, name='get_users'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),

    # Restaurant-related routes
    path('restaurants/', views.restaurants, name='restaurants'),
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),

    # Slot-related routes
    path('slots/', views.slots, name='slots'),
    path('slots/<int:slot_id>/', views.slot_detail, name='slot_detail'),

    # Table-related routes
    path('tables/', views.tables, name='tables'),
    path('tables/<int:table_id>/', views.table_detail, name='table_detail'),

    # Additional features
    path('available-dates/<int:restaurant_id>/', views.get_available_dates, name='available_dates'),
    path('find-available-tables/', views.find_available_tables, name='find_available_tables'),
    path('update-table-quantity/', views.update_table_quantity, name='update_table_quantity'),
]