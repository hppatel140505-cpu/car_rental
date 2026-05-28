from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('', views.home, name='home'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_details, name='car_details'),
    path('cars/<int:pk>/book/', views.book_car, name='book_car'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('bookings/<int:pk>/invoice/', views.view_invoice, name='view_invoice'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('policy/', views.rental_policy, name='policy'),
    # Custom Admin Section
    path('custom-admin/login/', views.admin_login, name='admin_login'),
    path('custom-admin/register/', views.admin_register, name='admin_register'),
    path('custom-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/bookings/', views.admin_bookings_list, name='admin_bookings'),
    path('custom-admin/bookings/<int:pk>/edit/', views.admin_booking_edit, name='admin_booking_edit'),
    path('custom-admin/bookings/<int:pk>/delete/', views.admin_booking_delete, name='admin_booking_delete'),
    path('custom-admin/bookings/<int:pk>/approve/', views.admin_booking_approve, name='admin_booking_approve'),
    path('custom-admin/bookings/<int:pk>/reject/', views.admin_booking_reject, name='admin_booking_reject'),
    path('custom-admin/bookings/<int:pk>/return/', views.admin_booking_return, name='admin_booking_return'),
    
    path('custom-admin/cars/', views.admin_cars_list, name='admin_cars'),
    path('custom-admin/cars/add/', views.admin_car_add, name='admin_car_add'),
    path('custom-admin/cars/<int:pk>/edit/', views.admin_car_edit, name='admin_car_edit'),
    path('custom-admin/cars/<int:pk>/delete/', views.admin_car_delete, name='admin_car_delete'),
    
    path('custom-admin/vehicles/', views.admin_vehicles_list, name='admin_vehicles'),
    path('custom-admin/vehicles/add/', views.admin_vehicle_add, name='admin_vehicle_add'),
    path('custom-admin/vehicles/<int:pk>/edit/', views.admin_vehicle_edit, name='admin_vehicle_edit'),
    path('custom-admin/vehicles/<int:pk>/delete/', views.admin_vehicle_delete, name='admin_vehicle_delete'),
    
    path('custom-admin/cartypes/', views.admin_cartypes_list, name='admin_cartypes'),
    path('custom-admin/cartypes/add/', views.admin_cartype_add, name='admin_cartype_add'),
    path('custom-admin/cartypes/<int:pk>/edit/', views.admin_cartype_edit, name='admin_cartype_edit'),
    path('custom-admin/cartypes/<int:pk>/delete/', views.admin_cartype_delete, name='admin_cartype_delete'),
]
