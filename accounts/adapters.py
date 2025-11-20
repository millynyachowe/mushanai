"""
Custom adapters for django-allauth
Handles social account signup and user creation
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter to handle Google OAuth signup
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed.
        
        This is where we can link existing accounts or set user attributes.
        """
        # If the user is already logged in, link the social account
        if request.user.is_authenticated:
            return
        
        # Try to find existing user by email
        if sociallogin.account.provider == 'google':
            email = sociallogin.account.extra_data.get('email')
            if email:
                try:
                    user = User.objects.get(email=email)
                    # Connect the social account to the existing user
                    sociallogin.connect(request, user)
                except User.DoesNotExist:
                    pass
    
    def populate_user(self, request, sociallogin, data):
        """
        Populates user information from social provider info.
        Called during the signup process.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Get additional data from Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            
            # Set user attributes from Google data
            user.email = extra_data.get('email', '')
            
            # Split the name into first_name and last_name
            full_name = extra_data.get('name', '')
            if full_name:
                name_parts = full_name.split(' ', 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
            else:
                user.first_name = extra_data.get('given_name', '')
                user.last_name = extra_data.get('family_name', '')
            
            # Set default user_type to CUSTOMER for Google signups
            if not user.user_type:
                user.user_type = 'CUSTOMER'
            
            # Mark email as verified since it's from Google
            user.email_verified = True
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Saves a new user account.
        Called during the signup process.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Additional processing after user is saved
        if sociallogin.account.provider == 'google':
            # You can add additional logic here
            # For example, sending a welcome email, creating profile, etc.
            pass
        
        return user


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for regular (non-social) account operations
    """
    
    def save_user(self, request, user, form, commit=True):
        """
        Saves a new user instance using information provided in the signup form.
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Set default user_type to CUSTOMER for regular signups
        if not user.user_type:
            user.user_type = 'CUSTOMER'
        
        if commit:
            user.save()
        
        return user

