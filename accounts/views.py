from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import User, UserProfile
from vendors.models import VendorProfile


def vendor_signup(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            phone_number = request.POST.get('phone_number', '')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            
            # Validation
            if not username or not email or not password:
                messages.error(request, 'Username, email, and password are required.')
                return render(request, 'accounts/vendor_signup.html')
            
            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different username.')
                return render(request, 'accounts/vendor_signup.html')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered. Please use a different email or login.')
                return render(request, 'accounts/vendor_signup.html')
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                user_type='VENDOR'
            )
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Create vendor profile
            company_name = f"{first_name} {last_name}'s Business" if first_name or last_name else f"{username}'s Business"
            VendorProfile.objects.create(
                vendor=user,
                company_name=company_name
            )
            
            # Log the user in (specify backend for django-allauth compatibility)
            from django.contrib.auth import get_backends
            backend = get_backends()[0]
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
            login(request, user, backend=user.backend)
            messages.success(request, 'Vendor account created successfully! Please complete your profile.')
            return redirect('vendor_dashboard')
            
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Vendor signup error: {str(e)}', exc_info=True)
            messages.error(request, f'An error occurred during signup. Please try again or contact support.')
            return render(request, 'accounts/vendor_signup.html')
    
    return render(request, 'accounts/vendor_signup.html')


def customer_signup(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            phone_number = request.POST.get('phone_number', '')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            
            # Validation
            if not username or not email or not password:
                messages.error(request, 'Username, email, and password are required.')
                return render(request, 'accounts/customer_signup.html')
            
            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different username.')
                return render(request, 'accounts/customer_signup.html')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered. Please use a different email or login.')
                return render(request, 'accounts/customer_signup.html')
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                user_type='CUSTOMER'
            )
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Create customer dashboard and impact metrics
            from customers.models import CustomerDashboard, CustomerImpactMetrics
            CustomerDashboard.objects.create(customer=user)
            CustomerImpactMetrics.objects.create(customer=user)
            
            # Create loyalty account
            from loyalty.models import LoyaltyAccount
            LoyaltyAccount.objects.create(customer=user)
            
            # Log the user in (specify backend for django-allauth compatibility)
            from django.contrib.auth import get_backends
            backend = get_backends()[0]
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
            login(request, user, backend=user.backend)
            messages.success(request, 'Customer account created successfully!')
            return redirect('customer_portal')
            
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Customer signup error: {str(e)}', exc_info=True)
            messages.error(request, f'An error occurred during signup. Please try again or contact support.')
            return render(request, 'accounts/customer_signup.html')
    
    return render(request, 'accounts/customer_signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.user_type == 'VENDOR':
                return redirect('vendor_dashboard')
            elif user.user_type == 'CUSTOMER':
                return redirect('customer_portal')
            else:
                return redirect('admin:index')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
