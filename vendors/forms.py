from django import forms
from django.forms import modelformset_factory

from .models import VendorPaymentOption, VendorProfile, VendorDeliveryZone


class VendorPaymentOptionForm(forms.ModelForm):
    class Meta:
        model = VendorPaymentOption
        fields = ['payment_type', 'is_enabled', 'phone_number', 'merchant_name', 'instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 2}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g., 0771234567'}),
            'merchant_name': forms.TextInput(attrs={'placeholder': 'Name as it appears on mobile wallet transfers'}),
        }
        labels = {
            'phone_number': 'Payment Phone Number',
            'merchant_name': 'Merchant/Account Name',
            'instructions': 'Payment Instructions (Optional)',
        }
        help_texts = {
            'merchant_name': 'Enter the exact name as it appears when customers send money to your account',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_type'].disabled = True
        
        # Make merchant_name required for mobile wallets
        if self.instance and self.instance.payment_type in ['ECOCASH', 'ONEMONEY', 'INNBUCKS']:
            self.fields['merchant_name'].required = True
        elif self.instance and self.instance.payment_type == 'CASH_ON_DELIVERY':
            self.fields['merchant_name'].required = False
            self.fields['phone_number'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        phone_number = cleaned_data.get('phone_number')
        merchant_name = cleaned_data.get('merchant_name')
        
        if payment_type in ['ECOCASH', 'ONEMONEY', 'INNBUCKS']:
            if not phone_number:
                self.add_error('phone_number', 'Phone number is required for mobile wallet payments.')
            if not merchant_name:
                self.add_error('merchant_name', 'Merchant name is required for mobile wallet payments. Enter the exact name as it appears when customers send money.')
        return cleaned_data


VendorPaymentOptionFormSet = modelformset_factory(
    VendorPaymentOption,
    form=VendorPaymentOptionForm,
    extra=0,
    can_delete=False
)


class VendorDeliverySettingsForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = [
            'delivery_free_city',
            'delivery_free_radius_km',
            'delivery_base_fee',
            'delivery_per_km_fee',
            'location_address',
            'location_latitude',
            'location_longitude',
            'harare_radius_km',
            'harare_within_radius_fee',
            'harare_beyond_radius_fee',
        ]
        labels = {
            'delivery_free_city': 'Free delivery city',
            'delivery_free_radius_km': 'Free delivery radius (km)',
            'delivery_base_fee': 'Base delivery fee (USD)',
            'delivery_per_km_fee': 'Additional fee per km (USD)',
            'location_address': 'Your business location address',
            'location_latitude': 'Latitude (optional - for automatic distance calculation)',
            'location_longitude': 'Longitude (optional - for automatic distance calculation)',
            'harare_radius_km': 'Harare free radius (km)',
            'harare_within_radius_fee': 'Fee within Harare radius',
            'harare_beyond_radius_fee': 'Fee for Harare deliveries beyond radius',
        }
        widgets = {
            'delivery_free_city': forms.TextInput(attrs={'placeholder': 'e.g., Harare'}),
            'delivery_free_radius_km': forms.NumberInput(attrs={'step': '0.1'}),
            'delivery_base_fee': forms.NumberInput(attrs={'step': '0.01'}),
            'delivery_per_km_fee': forms.NumberInput(attrs={'step': '0.01'}),
            'location_address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., 123 Main Street, Harare, Zimbabwe'}),
            'location_latitude': forms.NumberInput(attrs={'step': '0.000001', 'placeholder': 'e.g., -17.8292'}),
            'location_longitude': forms.NumberInput(attrs={'step': '0.000001', 'placeholder': 'e.g., 31.0522'}),
            'harare_radius_km': forms.NumberInput(attrs={'step': '0.1'}),
            'harare_within_radius_fee': forms.NumberInput(attrs={'step': '0.01'}),
            'harare_beyond_radius_fee': forms.NumberInput(attrs={'step': '0.01'}),
        }
        help_texts = {
            'location_address': 'Enter your business address. Click on the map to set your exact location.',
            'location_latitude': 'Automatically set when you click on the map.',
            'location_longitude': 'Automatically set when you click on the map.',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        location_address = cleaned_data.get('location_address')
        location_latitude = cleaned_data.get('location_latitude')
        location_longitude = cleaned_data.get('location_longitude')
        
        # Require location address and coordinates
        if not location_address:
            self.add_error('location_address', 'Business location address is required for delivery distance calculation.')
        if not location_latitude or not location_longitude:
            self.add_error('location_latitude', 'Please set your location on the map. Location coordinates are required.')
        
        return cleaned_data


class VendorDeliveryZoneForm(forms.ModelForm):
    class Meta:
        model = VendorDeliveryZone
        fields = ['city', 'fee', 'is_active']
        widgets = {
            'city': forms.HiddenInput(),
            'fee': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Enter fee in USD'}),
        }
        labels = {
            'fee': 'Delivery Fee (USD)',
            'is_active': 'Enable',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        is_active = cleaned_data.get('is_active')
        fee = cleaned_data.get('fee')
        if is_active and not fee:
            self.add_error('fee', 'Please set a delivery fee for this city or disable the option.')
        return cleaned_data


VendorDeliveryZoneFormSet = modelformset_factory(
    VendorDeliveryZone,
    form=VendorDeliveryZoneForm,
    extra=0,
    can_delete=False
)

