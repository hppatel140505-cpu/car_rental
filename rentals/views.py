from django.shortcuts import render, redirect, get_object_or_404
from .models import Car, CarType, Booking, Vehicle
from .forms import BookingForm, CarForm, CarTypeForm, AdminBookingForm, VehicleForm, CustomerRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, F, Sum, Count



def home(request):
    cars = Car.objects.filter(is_under_maintenance=False)[:4]
    return render(request, 'rentals/home.html', {'cars': cars})


def car_list(request):
    cars = Car.objects.filter(is_under_maintenance=False)
    categories = CarType.objects.all()
    return render(request, 'rentals/cars.html', {
        'cars': cars,
        'categories': categories,
    })


def car_details(request, pk):
    car = get_object_or_404(Car, pk=pk)
    form = BookingForm()
    return render(request, 'rentals/car_details.html', {
        'car': car,
        'form': form,
    })


@login_required
def book_car(request, pk):
    if request.user.is_staff:
        messages.error(request, "❌ Administrators are not permitted to make customer car bookings. Please use a standard customer account.")
        return redirect('rentals:car_details', pk=pk)
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            if car.stock >= 1:
                cd = form.cleaned_data
                days = cd.get('days', 1) or 1
                assigned_vehicle = car.vehicles.filter(is_available=True).first()
                Booking.objects.create(
                    user=request.user,
                    car=car,
                    vehicle=assigned_vehicle,
                    days=days,
                    pickup_date=cd['pickup_date'],
                    pickup_time=cd['pickup_time'],
                    return_date=cd['return_date'],
                    pickup_address=cd['pickup_address'],
                    status='Approved',
                )
                if assigned_vehicle:
                    assigned_vehicle.is_available = False
                    assigned_vehicle.save()
                messages.success(request, f"✅ Booking confirmed! {car.name} from {cd['pickup_date']} to {cd['return_date']}.")
                return redirect('rentals:my_bookings')
            else:
                messages.error(request, "❌ This car is not available right now.")
                return redirect('rentals:car_details', pk=pk)
        else:
            # Form invalid — re-render detail page with errors
            messages.error(request, "⚠️ Please fix the errors below.")
            return render(request, 'rentals/car_details.html', {
                'car': car,
                'form': form,
            })
    return redirect('rentals:car_details', pk=pk)


@login_required
def my_bookings(request):
    if request.user.is_staff:
        messages.warning(request, "🛡️ Administrators cannot access customer bookings. Please use the Admin Control Center.")
        return redirect('rentals:admin_dashboard')
    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    today = timezone.now().date()
    for booking in bookings:
        booking.is_past = booking.return_date and booking.return_date < today
    return render(request, 'rentals/bookings.html', {'bookings': bookings, 'today': today})


@login_required
def cancel_booking(request, pk):
    if request.user.is_staff:
        messages.error(request, "❌ Action not allowed for administrators.")
        return redirect('rentals:home')
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        if booking.status == 'Pending':
            vehicle = booking.vehicle
            if vehicle:
                vehicle.is_available = True
                vehicle.save()
            booking.status = 'Cancelled'
            booking.save()
            messages.success(request, f"❌ Booking for {booking.car.name} has been cancelled successfully.")
        else:
            messages.error(request, "⚠️ You can only cancel bookings that are pending approval.")
    return redirect('rentals:my_bookings')


def register_view(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "🎉 Account created successfully! Please log in to continue.")
            return redirect('rentals:login')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'rentals/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('rentals:home')
        else:
            messages.error(request, "❌ Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'rentals/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('rentals:home')


def admin_register(request):
    messages.error(request, "❌ Public registration of administrator accounts is disabled for security reasons.")
    return redirect('rentals:admin_login')


def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                if not user.is_staff:
                    messages.error(request, "❌ Access Denied: This account does not have administrator privileges.")
                    return redirect('rentals:admin_login')
                login(request, user)
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('rentals:admin_dashboard')
        else:
            messages.error(request, "❌ Invalid administrator credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'rentals/admin_login.html', {'form': form})


from functools import wraps

def custom_staff_member_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/custom-admin/login/?next={request.path}')
        if not request.user.is_staff:
            messages.error(request, "⚠️ Access Denied: Only staff accounts are permitted to view the Admin Dashboard.")
            return redirect('rentals:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ==============================================================================
# 📊 CUSTOM ADMIN / DASHBOARD VIEWS
# ==============================================================================

@custom_staff_member_required
def admin_dashboard(request):
    today = timezone.now().date()
    
    # KPI Calculations
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(return_date__gte=today).count()
    total_cars = Car.objects.count()
    total_users = User.objects.filter(is_staff=False).count()
    
    # Calculate total revenue
    revenue_agg = Booking.objects.annotate(
        cost=F('days') * F('car__price')
    ).aggregate(grand_total=Sum('cost'))
    total_revenue = revenue_agg['grand_total'] or 0.00
    
    # Recent Bookings & Low Stock Cars
    recent_bookings = Booking.objects.order_by('-booked_at')[:5]
    for booking in recent_bookings:
        booking.total_cost = booking.days * booking.car.price
        booking.is_past = booking.status == 'Returned' or booking.status == 'Cancelled' or (booking.return_date and booking.return_date < today)
        booking.is_running = booking.status == 'Approved' and booking.pickup_date and booking.return_date and (booking.pickup_date <= today <= booking.return_date)
        booking.is_upcoming = booking.status == 'Approved' and booking.pickup_date and booking.pickup_date > today
        
    low_stock_cars = Car.objects.annotate(
        available_count=Count('vehicles', filter=Q(vehicles__is_available=True))
    ).filter(available_count__lte=2).order_by('available_count')[:5]
    
    context = {
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'total_cars': total_cars,
        'total_users': total_users,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'low_stock_cars': low_stock_cars,
        'active_tab': 'dashboard',
    }
    return render(request, 'rentals/admin_dashboard.html', context)


@custom_staff_member_required
def admin_bookings_list(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    if not status_filter:
        status_filter = 'new'
    
    bookings = Booking.objects.all().order_by('-booked_at')
    
    if query:
        bookings = bookings.filter(
            Q(user__username__icontains=query) |
            Q(car__name__icontains=query) |
            Q(pickup_address__icontains=query)
        )
    
    today = timezone.now().date()
    if status_filter == 'new':
        bookings = bookings.filter(status='Approved')
    elif status_filter == 'upcoming':
        bookings = bookings.filter(status='Approved', pickup_date__gt=today)
    elif status_filter == 'running':
        bookings = bookings.filter(status='Approved', pickup_date__lte=today, return_date__gte=today)
    elif status_filter == 'history':
        # Complete history, no filter
        pass
    
    # Calculate costs and past state for templates
    for booking in bookings:
        booking.total_cost = booking.days * booking.car.price
        booking.is_past = booking.status == 'Returned' or booking.status == 'Cancelled' or (booking.return_date and booking.return_date < today)
        booking.is_running = booking.status == 'Approved' and booking.pickup_date and booking.return_date and (booking.pickup_date <= today <= booking.return_date)
        booking.is_upcoming = booking.status == 'Approved' and booking.pickup_date and booking.pickup_date > today
        
    context = {
        'bookings': bookings,
        'query': query,
        'status_filter': status_filter,
        'active_tab': 'bookings',
    }
    return render(request, 'rentals/admin_bookings.html', context)


@custom_staff_member_required
def admin_booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = AdminBookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Booking #{booking.id} for {booking.user.username} updated successfully!")
            return redirect('rentals:admin_bookings')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = AdminBookingForm(instance=booking)
    
    context = {
        'form': form,
        'booking': booking,
        'title': f"Edit Booking #{booking.id}",
        'active_tab': 'bookings',
    }
    return render(request, 'rentals/admin_booking_form.html', context)


@custom_staff_member_required
def admin_booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        vehicle = booking.vehicle
        if vehicle:
            vehicle.is_available = True
            vehicle.save()
        username = booking.user.username
        booking.delete()
        messages.success(request, f"❌ Booking #{pk} for {username} was successfully deleted/cancelled.")
        return redirect('rentals:admin_bookings')
    
    context = {
        'booking': booking,
        'active_tab': 'bookings',
    }
    return render(request, 'rentals/admin_booking_confirm_delete.html', context)


@custom_staff_member_required
def admin_cars_list(request):
    query = request.GET.get('q', '').strip()
    cars = Car.objects.all().order_by('-created_at')
    
    if query:
        cars = cars.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(description__icontains=query)
        )
        
    context = {
        'cars': cars,
        'query': query,
        'active_tab': 'cars',
    }
    return render(request, 'rentals/admin_cars.html', context)


@custom_staff_member_required
def admin_car_add(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save()
            plates_str = form.cleaned_data.get('initial_plate_numbers', '').strip()
            if plates_str:
                plates_list = [p.strip() for p in plates_str.split(',') if p.strip()]
                created_count = 0
                for plate in plates_list:
                    if not Vehicle.objects.filter(plate_number=plate).exists():
                        Vehicle.objects.create(car=car, plate_number=plate, is_available=True)
                        created_count += 1
                if created_count > 0:
                    messages.success(request, f"🟢 Added {created_count} physical vehicle unit(s) with plate numbers to the fleet!")
            
            messages.success(request, f"✅ Car '{car.name}' specification added successfully!")
            return redirect('rentals:admin_cars')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = CarForm()
    
    context = {
        'form': form,
        'title': "Add New Car",
        'active_tab': 'cars',
    }
    return render(request, 'rentals/admin_car_form.html', context)


@custom_staff_member_required
def admin_car_edit(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            plates_str = form.cleaned_data.get('initial_plate_numbers', '').strip()
            if plates_str:
                plates_list = [p.strip() for p in plates_str.split(',') if p.strip()]
                created_count = 0
                for plate in plates_list:
                    if not Vehicle.objects.filter(plate_number=plate).exists():
                        Vehicle.objects.create(car=car, plate_number=plate, is_available=True)
                        created_count += 1
                if created_count > 0:
                    messages.success(request, f"🟢 Added {created_count} new physical vehicle unit(s) to the fleet!")
            
            messages.success(request, f"✅ Car '{car.name}' specification updated successfully!")
            return redirect('rentals:admin_cars')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = CarForm(instance=car)
        
    context = {
        'form': form,
        'car': car,
        'title': f"Edit Car: {car.name}",
        'active_tab': 'cars',
    }
    return render(request, 'rentals/admin_car_form.html', context)


@custom_staff_member_required
def admin_car_delete(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        name = car.name
        car.delete()
        messages.success(request, f"❌ Car '{name}' has been successfully deleted.")
        return redirect('rentals:admin_cars')
        
    context = {
        'car': car,
        'active_tab': 'cars',
    }
    return render(request, 'rentals/admin_car_confirm_delete.html', context)


@custom_staff_member_required
def admin_vehicles_list(request):
    query = request.GET.get('q', '').strip()
    vehicles = Vehicle.objects.all().order_by('car__name', 'plate_number')
    
    if query:
        vehicles = vehicles.filter(
            Q(plate_number__icontains=query) |
            Q(car__name__icontains=query)
        )
        
    context = {
        'vehicles': vehicles,
        'query': query,
        'active_tab': 'vehicles',
    }
    return render(request, 'rentals/admin_vehicles.html', context)


@custom_staff_member_required
def admin_vehicle_add(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f"✅ Vehicle unit '{vehicle.plate_number}' added successfully!")
            return redirect('rentals:admin_vehicles')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = VehicleForm()
        
    context = {
        'form': form,
        'title': "Add Physical Vehicle (Plate Number)",
        'active_tab': 'vehicles',
    }
    return render(request, 'rentals/admin_vehicle_form.html', context)


@custom_staff_member_required
def admin_vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Vehicle unit '{vehicle.plate_number}' updated successfully!")
            return redirect('rentals:admin_vehicles')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = VehicleForm(instance=vehicle)
        
    context = {
        'form': form,
        'vehicle': vehicle,
        'title': f"Edit Vehicle: {vehicle.plate_number}",
        'active_tab': 'vehicles',
    }
    return render(request, 'rentals/admin_vehicle_form.html', context)


@custom_staff_member_required
def admin_vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        plate = vehicle.plate_number
        vehicle.delete()
        messages.success(request, f"❌ Vehicle '{plate}' has been successfully deleted from fleet.")
        return redirect('rentals:admin_vehicles')
        
    context = {
        'vehicle': vehicle,
        'active_tab': 'vehicles',
    }
    return render(request, 'rentals/admin_vehicle_confirm_delete.html', context)


@custom_staff_member_required
def admin_cartypes_list(request):
    query = request.GET.get('q', '').strip()
    cartypes = CarType.objects.all().order_by('name')
    
    if query:
        cartypes = cartypes.filter(name__icontains=query)
        
    context = {
        'cartypes': cartypes,
        'query': query,
        'active_tab': 'cartypes',
    }
    return render(request, 'rentals/admin_cartypes.html', context)


@custom_staff_member_required
def admin_cartype_add(request):
    if request.method == 'POST':
        form = CarTypeForm(request.POST)
        if form.is_valid():
            cartype = form.save()
            messages.success(request, f"🏷️ Category '{cartype.name}' created successfully!")
            return redirect('rentals:admin_cartypes')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = CarTypeForm()
        
    context = {
        'form': form,
        'title': "Add New Car Category",
        'active_tab': 'cartypes',
    }
    return render(request, 'rentals/admin_cartype_form.html', context)


@custom_staff_member_required
def admin_cartype_edit(request, pk):
    cartype = get_object_or_404(CarType, pk=pk)
    if request.method == 'POST':
        form = CarTypeForm(request.POST, instance=cartype)
        if form.is_valid():
            form.save()
            messages.success(request, f"🏷️ Category '{cartype.name}' updated successfully!")
            return redirect('rentals:admin_cartypes')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = CarTypeForm(instance=cartype)
        
    context = {
        'form': form,
        'cartype': cartype,
        'title': f"Edit Category: {cartype.name}",
        'active_tab': 'cartypes',
    }
    return render(request, 'rentals/admin_cartype_form.html', context)


@custom_staff_member_required
def admin_cartype_delete(request, pk):
    cartype = get_object_or_404(CarType, pk=pk)
    if request.method == 'POST':
        name = cartype.name
        cartype.delete()
        messages.success(request, f"❌ Category '{name}' deleted successfully.")
        return redirect('rentals:admin_cartypes')
        
    context = {
        'cartype': cartype,
        'active_tab': 'cartypes',
    }
    return render(request, 'rentals/admin_cartype_confirm_delete.html', context)


@custom_staff_member_required
def admin_booking_approve(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status == 'Pending':
        booking.status = 'Approved'
        booking.save()
        messages.success(request, f"🟢 Booking #{booking.id} for {booking.user.username} has been approved successfully!")
    else:
        messages.warning(request, f"Booking #{booking.id} is not in Pending status.")
    return redirect('rentals:admin_bookings')


@custom_staff_member_required
def admin_booking_reject(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status == 'Pending':
        booking.status = 'Cancelled'
        booking.save()
        # Return vehicle back to available fleet
        vehicle = booking.vehicle
        if vehicle:
            vehicle.is_available = True
            vehicle.save()
        messages.success(request, f"❌ Booking #{booking.id} for {booking.user.username} was rejected/cancelled and vehicle returned to availability.")
    else:
        messages.warning(request, f"Booking #{booking.id} is not in Pending status.")
    return redirect('rentals:admin_bookings')


@custom_staff_member_required
def admin_booking_return(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status == 'Approved':
        booking.status = 'Returned'
        booking.save()
        # Return vehicle back to available fleet
        vehicle = booking.vehicle
        if vehicle:
            vehicle.is_available = True
            vehicle.save()
        messages.success(request, f"✅ Booking #{booking.id} marked as Returned! Vehicle is now available for next booking.")
    else:
        messages.warning(request, f"Booking #{booking.id} is not in Approved status.")
    return redirect('rentals:admin_bookings')


@login_required
def view_invoice(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    # Check permission: booked user or staff user only
    if not request.user.is_staff and booking.user != request.user:
        messages.error(request, "⚠️ Permission Denied: You cannot view invoices for other customers.")
        return redirect('rentals:home')
        
    if booking.status not in ['Approved', 'Returned']:
        messages.error(request, "⚠️ Invoices are only generated for approved or completed bookings.")
        return redirect('rentals:my_bookings')
        
    booking.total_cost = booking.days * booking.car.price
    context = {
        'booking': booking,
    }
    return render(request, 'rentals/invoice.html', context)


def rental_policy(request):
    return render(request, 'rentals/policy.html')


