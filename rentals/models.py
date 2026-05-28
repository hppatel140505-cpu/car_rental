from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class CarType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Car Type")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    class Meta:
        verbose_name = "Car Type"
        verbose_name_plural = "Car Types"

    def __str__(self):
        return self.name


class Car(models.Model):
    category = models.ForeignKey(
        CarType, related_name='cars', on_delete=models.CASCADE,
        verbose_name="Car Type"
    )
    name = models.CharField(max_length=200, verbose_name="Car Name / Model")
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Rent per Day (₹)")
    image = models.ImageField(upload_to='cars/', blank=True, null=True, verbose_name="Car Image")
    FUEL_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric (EV)', 'Electric (EV)'),
        ('CNG', 'CNG'),
        ('Hybrid', 'Hybrid'),
    ]
    fuel_type = models.CharField(max_length=50, choices=FUEL_CHOICES, default='Petrol', verbose_name="Fuel Type")
    seats = models.PositiveIntegerField(default=5, verbose_name="Seats Count")
    ac = models.BooleanField(default=True, verbose_name="Air Conditioning (AC)")
    luggage = models.PositiveIntegerField(default=2, verbose_name="Luggage Capacity (Bags)")
    is_under_maintenance = models.BooleanField(default=False, verbose_name="Under Maintenance")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Listed On")

    class Meta:
        verbose_name = "Car"
        verbose_name_plural = "Cars"

    def __str__(self):
        return f"{self.name} — ₹{self.price}/day"

    @property
    def stock(self):
        if self.is_under_maintenance:
            return 0
        return self.vehicles.filter(is_available=True).count()


class Vehicle(models.Model):
    car = models.ForeignKey(
        Car, related_name='vehicles', on_delete=models.CASCADE,
        verbose_name="Car Model"
    )
    plate_number = models.CharField(max_length=50, unique=True, verbose_name="Plate Number")
    is_available = models.BooleanField(default=True, verbose_name="Is Available")

    class Meta:
        verbose_name = "Physical Vehicle"
        verbose_name_plural = "Physical Vehicles"

    def __str__(self):
        return f"{self.car.name} — ({self.plate_number})"


STATUS_CHOICES = [
    ('Approved', 'Running'),
    ('Returned', 'Returned / Available'),
    ('Cancelled', 'Cancelled'),
]


class Booking(models.Model):
    user = models.ForeignKey(
        User, related_name='bookings', on_delete=models.CASCADE,
        verbose_name="Customer"
    )
    car = models.ForeignKey(
        Car, related_name='bookings', on_delete=models.CASCADE,
        verbose_name="Car Booked"
    )
    vehicle = models.ForeignKey(
        Vehicle, related_name='bookings', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Assigned Vehicle"
    )
    days = models.PositiveIntegerField(default=1, verbose_name="Number of Days")
    pickup_date = models.DateField(null=True, blank=True, verbose_name="Pickup Date")
    pickup_time = models.TimeField(null=True, blank=True, verbose_name="Pickup Time")
    return_date = models.DateField(null=True, blank=True, verbose_name="Return Date")
    pickup_address = models.TextField(null=True, blank=True, verbose_name="Pickup Address")
    status = models.CharField(
        max_length=20, default='Approved', choices=STATUS_CHOICES,
        verbose_name="Status"
    )
    booked_at = models.DateTimeField(auto_now_add=True, verbose_name="Booked On")

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def __str__(self):
        assigned_plate = self.vehicle.plate_number if self.vehicle else "None Assigned"
        return f"{self.user.username} → {self.car.name} ({assigned_plate}) ({self.days} days — {self.status})"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile',
        verbose_name="User"
    )
    phone_number = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Phone Number"
    )

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} — {self.phone_number or 'No Phone'}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
