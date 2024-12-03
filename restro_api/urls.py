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

# urlpatterns = [
#     # Admin route
#     path('admin/', admin.site.urls),

#     # User-related routes
#     path('add-user/', views.add_user, name='add_user'),
#     path('users/', views.get_users, name='get_users'),
#     path('users/<int:user_id>/', views.user_detail, name='user_detail'),

#     # Restaurant-related routes
#     path('restaurants/', views.restaurants, name='restaurants'),
#     path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),

#     # Slot-related routes
#     path('slots/', views.slots, name='slots'),
#     path('slots/<int:slot_id>/', views.slot_detail, name='slot_detail'),

#     # Table-related routes
#     path('tables/', views.tables, name='tables'),
#     path('tables/<int:table_id>/', views.table_detail, name='table_detail'),

#     #Booking-related routes
#     path('booking/', views.add_booking, name='booking'),


#     # Additional features
#     path('available-dates/<int:restaurant_id>/', views.get_available_dates, name='available_dates'),
#     path('find-available-tables/', views.find_available_tables, name='find_available_tables'),
#     path('update-table-quantity/', views.update_table_quantity, name='update_table_quantity'),
# ]

urlpatterns = [
    # Admin route
    path('admin/', admin.site.urls),

    path('login/', views.login_user, name='login_user'),
    
    # User-related routes
    path('users/', views.get_users, name='get_users'),  # Get all users
    path('users/add/', views.add_user, name='add_user'),  # Add a user
    path('users/<str:email>/', views.user_detail, name='user_detail'),  # User detail operations (GET, PUT, DELETE)

    # Restaurant-related routes
    path('restaurants/', views.restaurants, name='restaurants'),  # List all or add a restaurant
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),  # Restaurant detail operations

    # Slot-related routes
    path('restaurants/<int:restaurant_id>/slots/', views.slots, name='slots'),  # Slots for a specific restaurant
    path('restaurants/<int:restaurant_id>/slots/<int:slot_id>/', views.slot_detail, name='slot_detail'),  # Slot detail operations

    path('restaurants/<int:restaurant_id>/slots/auto-create/', views.auto_create_slots, name='auto_create_slots'), #automatic slot creation by date

    # Table-related routes
    path('restaurants/<int:restaurant_id>/tables/', views.restaurant_tables, name='restaurant_tables'),
    path('restaurants/<int:restaurant_id>/tables/bulk-add/', views.bulk_add_tables, name='bulk_add_tables'),
    path('restaurants/<int:restaurant_id>/tables/<int:table_id>/', views.restaurant_table_detail, name='restaurant_table_detail'),

    # Booking-related routes
    path('restaurants/<int:restaurant_id>/slots/<int:slot_id>/book/', views.book_table, name='book_table'),  # Booking a table for a specific slot

    # Additional features
    # path('restaurants/<int:restaurant_id>/available-dates/', views.get_available_dates, name='available_dates'),  # Get available dates for a restaurant
    # path('restaurants/<int:restaurant_id>/find-available-tables/', views.find_available_tables, name='find_available_tables'),  # Find available tables for a restaurant
    # path('restaurants/<int:restaurant_id>/update-table-quantity/', views.update_table_quantity, name='update_table_quantity'),  # Update table quantities
]
