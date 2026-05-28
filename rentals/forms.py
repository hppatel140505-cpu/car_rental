from django import forms
from .models import Booking, Car, CarType, Vehicle, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import datetime


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. customer@example.com',
            'autocomplete': 'email',
        })
    )
    phone_number = forms.CharField(
        required=True,
        max_length=15,
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. +91 98765 43210',
            'autocomplete': 'tel',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        # Allow digits, spaces, +, -, (, )
        import re
        if not re.match(r'^[\+\d][\d\s\-\(\)]{6,14}$', phone):
            raise forms.ValidationError("Enter a valid phone number (7–15 digits).")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Save phone number to profile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.save()
        return user



class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['pickup_date', 'pickup_time', 'return_date', 'pickup_address']
        widgets = {
            'pickup_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-input',
                    'min': datetime.date.today().isoformat(),
                }
            ),
            'pickup_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-input',
                }
            ),
            'return_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-input',
                    'min': datetime.date.today().isoformat(),
                }
            ),
            'pickup_address': forms.Textarea(
                attrs={
                    'class': 'form-input',
                    'rows': 3,
                    'placeholder': 'e.g. 123 MG Road, Ahmedabad, Gujarat 380001',
                }
            ),
        }
        labels = {
            'pickup_date':    'Pickup Date',
            'pickup_time':    'Pickup Time',
            'return_date':    'Return Date',
            'pickup_address': 'Pickup Address',
        }

    def clean(self):
        cleaned = super().clean()
        pickup = cleaned.get('pickup_date')
        ret    = cleaned.get('return_date')

        if pickup and ret:
            if ret <= pickup:
                raise forms.ValidationError("Return date must be after pickup date.")
            diff = (ret - pickup).days
            cleaned['days'] = diff
        return cleaned


class CarForm(forms.ModelForm):
    initial_plate_numbers = forms.CharField(
        required=False,
        label="Add Physical Vehicle Plate Numbers",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. GJ-01-XX-1234, GJ-01-XX-5678 (comma separated)'
        }),
        help_text="Provide comma-separated license plate numbers to instantly register physical vehicles of this model."
    )

    class Meta:
        model = Car
        fields = ['category', 'name', 'description', 'price', 'fuel_type', 'seats', 'ac', 'luggage', 'is_under_maintenance', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. BMW M4 Coupe'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Detailed specifications...'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '₹ Price per day'}),
            'fuel_type': forms.Select(attrs={'class': 'form-input'}),
            'seats': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'placeholder': 'e.g. 5'}),
            'ac': forms.CheckboxInput(attrs={'class': 'form-checkbox-input'}),
            'luggage': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'placeholder': 'e.g. 2'}),
            'is_under_maintenance': forms.CheckboxInput(attrs={'class': 'form-checkbox-input'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # Creation mode: plate numbers are REQUIRED
            self.fields['initial_plate_numbers'].required = True
            self.fields['initial_plate_numbers'].label = "Add Physical Vehicle Plate Numbers (Required)"
        else:
            # Editing mode: plate numbers are optional
            self.fields['initial_plate_numbers'].required = False
            self.fields['initial_plate_numbers'].label = "Add Additional Plate Numbers (Optional)"


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['car', 'plate_number', 'is_available']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-input'}),
            'plate_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. GJ-01-XX-1234'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-checkbox-input'}),
        }


class CarTypeForm(forms.ModelForm):
    class Meta:
        model = CarType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. SUV, Luxury, Sedan'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Brief description of category...'}),
        }


class AdminBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user', 'car', 'vehicle', 'status', 'days', 'pickup_date', 'pickup_time', 'return_date', 'pickup_address']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-input'}),
            'car': forms.Select(attrs={'class': 'form-input'}),
            'vehicle': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'days': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'pickup_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'pickup_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'return_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'pickup_address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'e.g. Pickup Location Address'}),
        }

    def clean(self):
        cleaned = super().clean()
        pickup = cleaned.get('pickup_date')
        ret    = cleaned.get('return_date')

        if pickup and ret:
            if ret <= pickup:
                raise forms.ValidationError("Return date must be after pickup date.")
            diff = (ret - pickup).days
            cleaned['days'] = diff
        return cleaned

