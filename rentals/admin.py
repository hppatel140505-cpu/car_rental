from django.contrib import admin
from .models import CarType, Car, Booking, Vehicle


@admin.register(CarType)
class CarTypeAdmin(admin.ModelAdmin):
    list_display  = ['name', 'description']
    search_fields = ['name']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display        = ['name', 'category', 'price', 'stock', 'created_at']
    list_filter         = ['category']
    search_fields       = ['name', 'description']
    list_editable       = ['price']
    readonly_fields     = ['created_at', 'stock']
    fieldsets = (
        ("Car Details", {
            'fields': ('name', 'category', 'description', 'image')
        }),
        ("⚙️ Specifications", {
            'fields': ('fuel_type', 'seats', 'ac', 'luggage')
        }),
        ("💰 Pricing & Availability", {
            'fields': ('price', 'stock')
        }),
        ("📅 Meta", {
            'fields': ('created_at',)
        }),
    )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display  = ['plate_number', 'car', 'is_available']
    list_filter   = ['is_available', 'car']
    search_fields = ['plate_number', 'car__name']
    list_editable = ['is_available']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'car', 'vehicle', 'days', 'status', 'booked_at']
    list_filter   = ['status', 'booked_at', 'car__category']
    search_fields = ['user__username', 'car__name', 'vehicle__plate_number']
    readonly_fields = ['booked_at']
