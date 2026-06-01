# Car Rental System

A feature-rich Car Rental System built using Django. This project allows users to browse available cars, make bookings, and view their invoices. It also includes a custom admin dashboard for managing cars, physical vehicles, car types, and user bookings.

## 🚀 Features

### User Features
- **Authentication:** User registration, login, and logout.
- **Car Browsing:** View all available cars and their detailed specifications (fuel type, seats, luggage capacity, pricing, etc.).
- **Bookings:** Book a car for specific dates, view current bookings, cancel bookings, and view booking invoices.
- **Rental Policy:** Access to rental terms and conditions.

### Custom Admin Dashboard
- **Booking Management:** Approve, reject, edit, delete, or mark bookings as returned.
- **Car Management:** Add, update, and delete car models.
- **Vehicle Management:** Manage physical vehicles by their number plates to keep track of real-world stock and availability.
- **Car Types Management:** Categorize cars (e.g., SUV, Sedan, Hatchback).

## 🛠️ Tech Stack
- **Backend:** Python, Django 4.2
- **Database:** SQLite3 (default)
- **Image Handling:** Pillow

## ⚙️ Installation and Setup

Follow these steps to set up the project on your local machine:

### 1. Prerequisites
Make sure you have Python installed on your system. You can download it from [python.org](https://www.python.org/).

### 2. Navigate to the Project Directory
Open your terminal or command prompt and navigate to the root directory of the project:
```bash
cd path/to/car_rental
```

### 3. Create a Virtual Environment
It is highly recommended to use a virtual environment to manage project dependencies so they don't interfere with your system Python packages.
```bash
python -m venv venv
```

### 4. Activate the Virtual Environment
- **On Windows:**
  ```cmd
  venv\Scripts\activate
  ```
- **On macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 5. Install Dependencies
Install all the required Python packages mentioned in the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 6. Apply Database Migrations
Create the necessary database tables based on the Django models:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a Superuser (Admin Account)
Create an admin account to access the custom admin dashboard and the Django default admin:
```bash
python manage.py createsuperuser
```
Follow the prompts to set a username, email, and password.

### 8. Run the Development Server
Start the local development server:
```bash
python manage.py runserver
```

### 9. Access the Application
Open your web browser and navigate to:
- **Main Website:** `http://127.0.0.1:8000/`
- **Custom Admin Login:** `http://127.0.0.1:8000/custom-admin/login/`
- **Default Django Admin:** `http://127.0.0.1:8000/admin/`

## 📁 Project Structure Highlights
- `car_rental/`: Main project configuration folder (settings, main URLs).
- `rentals/`: The core application containing models, views, and URLs for both users and the custom admin dashboard.
- `media/`: Directory where uploaded files (like car images) are stored.
- `static/`: Contains static files like CSS, JS, and UI images.
- `templates/`: HTML templates for the website's frontend.