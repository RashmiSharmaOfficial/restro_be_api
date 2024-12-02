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
    path('admin/', admin.site.urls),
     path('add-user/', views.AddUserView.as_view(), name='add_user'),
    path('users/', views.GetUsersView.as_view(), name='get_users'),
    path('users/<int:user_id>/', views.GetUserView.as_view(), name='get_user'),
    path('users/<int:user_id>/update/', views.UpdateUserView.as_view(), name='update_user'),
    path('users/<int:user_id>/delete/', views.DeleteUserView.as_view(), name='delete_user'),
    path('restaurants/', views.RestaurantListCreate.as_view(), name='restaurant_list_create'),
    path('restaurants/<int:pk>/', views.RestaurantDetail.as_view(), name='restaurant_detail'),
    path('slots/', views.SlotListCreate.as_view(), name='slot_list_create'),
    path('slots/<int:pk>/', views.SlotDetail.as_view(), name='slot_detail'),
    path('tables/', views.get_tables, name='get_tables'),  # GET all tables
    path('tables/<int:pk>/', views.get_table, name='get_table'),  # GET specific table by ID
    path('add-table/', views.add_table, name='add_table'),  # POST create a table
    path('update-table/<int:pk>/', views.update_table, name='update_table'),  # PUT update a table
    path('delete-table/<int:pk>/', views.delete_table, name='delete_table'),  # DELETE a table
   # Endpoint to get available dates and slots for a restaurant
    path('available-dates/<int:restaurant_id>/', views.get_available_dates, name='available_dates'),
    
    # Endpoint to find available tables for a selected slot and number of people
    path('find-available-tables/', views.find_available_tables, name='find_available_tables'),
    
    # Endpoint to update table quantities after booking
    path('update-table-quantity/', views.update_table_quantity, name='update_table_quantity'),
]
