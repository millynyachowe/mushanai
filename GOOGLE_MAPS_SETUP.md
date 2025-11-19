# Google Maps Integration Setup

## Overview
The Mushanai platform now uses Google Maps for:
- **Vendor Location Selection**: Vendors set their business location on an interactive map
- **Customer Delivery Location**: Customers select their delivery address on a map during checkout
- **Automatic Distance Calculation**: Distance is calculated automatically using Google Maps Distance Matrix API

## Required Google Maps APIs

You need to enable the following APIs in your Google Cloud Console:

1. **Maps JavaScript API** - For displaying interactive maps
2. **Geocoding API** - For converting addresses to coordinates and vice versa
3. **Distance Matrix API** - For calculating accurate driving distances
4. **Places API** - For address autocomplete functionality

## Setup Instructions

### Step 1: Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the required APIs:
   - Navigate to "APIs & Services" > "Library"
   - Search for and enable:
     - Maps JavaScript API
     - Geocoding API
     - Distance Matrix API
     - Places API
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy your API key

### Step 2: Configure API Key Restrictions (Recommended for Production)

1. Click on your API key to edit it
2. Under "API restrictions", select "Restrict key"
3. Choose the APIs listed above
4. Under "Application restrictions", set restrictions as needed:
   - HTTP referrers (for web)
   - IP addresses (for server-side)

### Step 3: Add API Key to Django Settings

**Option 1: Environment Variable (Recommended)**
```bash
export GOOGLE_MAPS_API_KEY='your-api-key-here'
```

**Option 2: Direct in settings.py**
```python
GOOGLE_MAPS_API_KEY = 'your-api-key-here'
```

The key is already configured in `mushanaicore/settings.py` to read from environment variables:
```python
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
```

## Features

### Vendor Location Setup
- Vendors **must** set their business location in Payment Settings
- Interactive map with click-to-set location
- Address autocomplete for easy location entry
- Coordinates automatically saved when location is set

### Customer Checkout
- Interactive map showing vendor location (blue marker)
- Customer can click on map or search for address
- Distance calculated automatically using:
  - Google Maps Distance Matrix API (if available) - more accurate
  - Haversine formula (fallback) - straight-line distance
- Delivery fee calculated in real-time based on:
  - Base delivery fee
  - Free delivery radius (if set)
  - Per-kilometer fee beyond free radius

### Fallback Behavior
- If vendor hasn't set location: Customer sees warning and must enter distance manually
- If Google Maps API key not set: Map functionality disabled, manual entry required
- If Distance Matrix API fails: Falls back to Haversine formula calculation

## Cost Considerations - FREE TIER AVAILABLE! ✅

**Good News: Google Maps offers $200 in FREE credits per month!**

This means for most small to medium businesses, Google Maps is essentially **FREE**:

### Free Tier Coverage ($200/month credit):
- **Maps JavaScript API**: $7 per 1,000 loads = ~28,500 free map loads/month
- **Geocoding API**: $5 per 1,000 requests = ~40,000 free geocoding requests/month
- **Distance Matrix API**: $5 per 1,000 elements = ~40,000 free distance calculations/month
- **Places API**: $17 per 1,000 requests = ~11,700 free autocomplete requests/month

### What This Means:
- **Small business**: Likely 100% free (stays within $200 credit)
- **Medium business**: Mostly free, may pay a few dollars if you exceed
- **Large business**: Pay-as-you-go after $200 credit is used

### How to Stay Free:
1. Monitor usage in Google Cloud Console
2. Set up billing alerts (you'll only pay if you exceed $200)
3. The $200 credit resets every month automatically

### Pricing (after free tier):
- Maps JavaScript API: $7 per 1,000 loads
- Geocoding API: $5 per 1,000 requests
- Distance Matrix API: $5 per 1,000 elements
- Places API: $17 per 1,000 requests

**Note**: You need to add a payment method to Google Cloud, but you won't be charged unless you exceed $200/month.

## Testing

1. Set vendor location in Payment Settings
2. Add products to cart
3. Go to checkout
4. Verify map appears with vendor location
5. Click on map or search for address
6. Verify distance and delivery fee calculate automatically

## Troubleshooting

**Map not showing:**
- Check if API key is set correctly
- Verify APIs are enabled in Google Cloud Console
- Check browser console for errors

**Distance not calculating:**
- Verify Distance Matrix API is enabled
- Check API key has correct permissions
- Verify vendor has set their location

**Address autocomplete not working:**
- Verify Places API is enabled
- Check API key restrictions allow your domain

