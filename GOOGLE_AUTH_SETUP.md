# 🔐 Google OAuth Authentication - Setup Guide

## 🎉 WHAT WAS ADDED

Your Mushanai platform now supports **Google Sign-In**! Users can:
- ✅ Sign up with their Google account (one click!)
- ✅ Sign in with their Google account
- ✅ Link existing accounts to Google
- ✅ Skip email verification (Google handles it)
- ✅ Auto-populate profile data from Google

---

## 📦 WHAT WAS INSTALLED

### **New Dependencies:**

Added to `requirements.txt`:
```python
django-allauth==0.63.6      # Social authentication framework
requests==2.31.0            # HTTP library
oauthlib==3.2.2             # OAuth implementation
PyJWT==2.8.0                # JSON Web Token support
```

### **Django Apps Added:**

- `django.contrib.sites` - Sites framework
- `allauth` - Core allauth
- `allauth.account` - Account management
- `allauth.socialaccount` - Social account support
- `allauth.socialaccount.providers.google` - Google OAuth provider

---

## 🔧 CONFIGURATION DONE

### **1. Settings Updated** (`settings.py`)

✅ **Installed Apps:**
- Added django-allauth apps
- Added sites framework

✅ **Authentication Backends:**
- Django default backend (username/password)
- Allauth backend (email/social)

✅ **Allauth Settings:**
- Email-based authentication
- Optional email verification
- Auto-signup for social accounts
- Google OAuth configuration

✅ **Custom Adapter:**
- `accounts.adapters.CustomSocialAccountAdapter`
- Handles Google signup logic
- Auto-sets user_type to CUSTOMER
- Links existing accounts by email

### **2. URLs Updated** (`urls.py`)

✅ Added: `path('accounts/', include('allauth.urls'))`
- Handles OAuth callbacks
- Login/logout flows
- Social authentication

### **3. Templates Created**

✅ **`templates/account/login.html`**
- Google Sign In button
- Regular email/password login
- Beautiful, modern UI

✅ **`templates/account/signup.html`**
- Google Sign Up button
- Regular email/password signup
- Terms acceptance

✅ **`templates/account/logout.html`**
- Clean logout confirmation

### **4. Custom Adapter Created** (`accounts/adapters.py`)

✅ **Features:**
- Links Google accounts to existing users by email
- Auto-populates user data from Google
- Sets default user_type to CUSTOMER
- Marks email as verified

---

## 🚀 SETUP INSTRUCTIONS

### **Step 1: Install Dependencies**

```bash
cd /Users/ishe/Desktop/Milly/mushanai

# Install new packages
pip install -r requirements.txt

# Or install individually
pip install django-allauth==0.63.6 requests==2.31.0 oauthlib==3.2.2 PyJWT==2.8.0
```

### **Step 2: Run Migrations**

```bash
python manage.py migrate
```

This creates tables for:
- `django_site`
- `socialaccount_socialapp`
- `socialaccount_socialaccount`
- `socialaccount_socialtoken`

### **Step 3: Create Google OAuth App**

#### **3.1 Go to Google Cloud Console**

Visit: https://console.cloud.google.com/

#### **3.2 Create a Project**

1. Click "Select a project" → "New Project"
2. Project name: **Mushanai**
3. Click "Create"

#### **3.3 Enable Google+ API**

1. Go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click "Enable"

#### **3.4 Create OAuth Credentials**

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure consent screen (if prompted):
   - User Type: **External**
   - App name: **Mushanai**
   - User support email: Your email
   - Developer email: Your email
   - Click "Save and Continue"
   - Scopes: Click "Save and Continue" (default is fine)
   - Test users: Add your email
   - Click "Save and Continue"

4. Create OAuth Client ID:
   - Application type: **Web application**
   - Name: **Mushanai Web Client**
   - Authorized JavaScript origins:
     ```
     http://localhost:8000
     http://127.0.0.1:8000
     http://localhost
     ```
   - Authorized redirect URIs:
     ```
     http://localhost:8000/accounts/google/login/callback/
     http://127.0.0.1:8000/accounts/google/login/callback/
     http://localhost/accounts/google/login/callback/
     ```
   - Click "Create"

5. **Copy your credentials:**
   - Client ID: `123456789-abcdefghijklmnop.apps.googleusercontent.com`
   - Client Secret: `GOCSPX-xxxxxxxxxxxxxxxxxxxxx`

#### **3.5 Add Credentials to .env**

Edit `/Users/ishe/Desktop/Milly/mushanai/.env`:

```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret-here
```

**IMPORTANT:** Never commit these to GitHub!

### **Step 4: Configure in Django Admin**

```bash
# Start your server
python manage.py runserver
```

1. Go to: http://localhost:8000/admin
2. Login with your superuser account
3. Go to "Sites" → Click on "example.com"
4. Change:
   - Domain name: `localhost:8000`
   - Display name: `Mushanai`
   - Click "Save"

5. Go to "Social applications" → "Add social application"
6. Fill in:
   - Provider: **Google**
   - Name: **Mushanai Google OAuth**
   - Client id: *Your Google Client ID*
   - Secret key: *Your Google Client Secret*
   - Sites: Select "Mushanai" and move it to "Chosen sites" →
   - Click "Save"

---

## ✅ TESTING

### **Test Google Sign In:**

1. Go to: http://localhost:8000/accounts/login/
2. Click "Continue with Google"
3. Select your Google account
4. Approve the permissions
5. You should be redirected back and logged in!

### **Test Regular Sign Up:**

1. Go to: http://localhost:8000/accounts/signup/
2. Fill in email and password
3. Click "Create Account"
4. You should be logged in!

### **Verify in Admin:**

1. Go to: http://localhost:8000/admin/accounts/user/
2. You should see the new user with:
   - Email from Google
   - Name from Google
   - user_type = CUSTOMER
   - email_verified = True

---

## 🎯 HOW IT WORKS

### **Google Sign In Flow:**

```
User clicks "Continue with Google"
          ↓
Redirects to Google OAuth
          ↓
User approves permissions
          ↓
Google redirects back with code
          ↓
Django exchanges code for token
          ↓
Django fetches user info from Google
          ↓
CustomSocialAccountAdapter processes:
  - Checks if email exists
  - Links to existing account OR creates new user
  - Sets user_type = CUSTOMER
  - Populates first_name, last_name from Google
  - Marks email_verified = True
          ↓
User is logged in!
          ↓
Redirects to home page (/)
```

### **Account Linking:**

If a user signs up with email/password first, then later uses "Sign in with Google" with the same email, the system will:
1. Find the existing account by email
2. Link the Google account to it
3. Log them in to their existing account

**No duplicate accounts created!**

---

## 🔒 SECURITY FEATURES

### **Built-in Security:**

✅ **CSRF Protection** - All forms protected  
✅ **State Parameter** - Prevents CSRF attacks on OAuth  
✅ **Secure Tokens** - Stored securely in database  
✅ **Email Verification** - Optional for regular signups  
✅ **Password Validation** - Django's built-in validators  
✅ **HTTPS Ready** - Works with SSL in production  

### **Data Privacy:**

- ✅ Only requests `profile` and `email` scopes
- ✅ Does not access Google Drive, Calendar, etc.
- ✅ User controls what data to share
- ✅ Can revoke access anytime from Google account settings

---

## 🌐 PRODUCTION DEPLOYMENT

### **Step 1: Add Production URLs**

In Google Cloud Console → Credentials → Edit OAuth Client:

Add your production URLs:
```
Authorized JavaScript origins:
- https://yourdomain.com
- https://www.yourdomain.com

Authorized redirect URIs:
- https://yourdomain.com/accounts/google/login/callback/
- https://www.yourdomain.com/accounts/google/login/callback/
```

### **Step 2: Update Django Site**

In Django Admin → Sites:
- Domain: `yourdomain.com`
- Display name: `Mushanai`

### **Step 3: Environment Variables**

Make sure `.env` has production values:
```env
SITE_URL=https://yourdomain.com
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-client-secret
DEBUG=False
```

### **Step 4: Publish OAuth App**

In Google Cloud Console:
1. OAuth consent screen
2. Click "Publish App"
3. Submit for verification (if needed)

---

## 🎨 CUSTOMIZATION

### **Change Redirect After Login:**

In `settings.py`:
```python
LOGIN_REDIRECT_URL = '/customer/dashboard/'  # Or wherever you want
```

### **Add More Social Providers:**

```bash
# Facebook
pip install django-allauth[facebook]

# Twitter/X
pip install django-allauth[twitter]

# GitHub
pip install django-allauth[github]
```

Then add to `INSTALLED_APPS`:
```python
'allauth.socialaccount.providers.facebook',
'allauth.socialaccount.providers.twitter',
'allauth.socialaccount.providers.github',
```

### **Customize Templates:**

Templates are in `templates/account/`:
- `login.html` - Login page
- `signup.html` - Signup page
- `logout.html` - Logout page
- `password_reset.html` - Password reset
- `email_confirm.html` - Email confirmation

Edit these to match your branding!

### **Custom User Creation Logic:**

Edit `accounts/adapters.py` → `CustomSocialAccountAdapter`:

```python
def populate_user(self, request, sociallogin, data):
    user = super().populate_user(request, sociallogin, data)
    
    # Your custom logic here
    # Example: Set user to VENDOR if email domain is @vendor.com
    if user.email.endswith('@vendor.com'):
        user.user_type = 'VENDOR'
    
    return user
```

---

## 📊 ADMIN MANAGEMENT

### **View Social Accounts:**

Django Admin → Social Accounts

Shows:
- User
- Provider (Google)
- UID (Google user ID)
- Date joined
- Extra data (profile info)

### **View Social Tokens:**

Django Admin → Social Application Tokens

Shows:
- App
- Account
- Token
- Token secret
- Expires at

### **Disconnect Social Account:**

Users can disconnect in Django Admin or you can build a UI for it:

```python
# In your view
from allauth.socialaccount.models import SocialAccount

def disconnect_google(request):
    SocialAccount.objects.filter(
        user=request.user,
        provider='google'
    ).delete()
    return redirect('profile')
```

---

## 🐛 TROUBLESHOOTING

### **Error: "Redirect URI mismatch"**

**Fix:** Make sure your redirect URI in Google Cloud Console exactly matches:
```
http://localhost:8000/accounts/google/login/callback/
```
Note the trailing slash!

### **Error: "Site matching query does not exist"**

**Fix:** Run migration and create site:
```bash
python manage.py migrate
python manage.py shell
>>> from django.contrib.sites.models import Site
>>> Site.objects.create(domain='localhost:8000', name='Mushanai')
```

### **Error: "SocialApp matching query does not exist"**

**Fix:** Go to Django Admin → Social Applications and create one with:
- Provider: Google
- Client ID: Your Google Client ID
- Secret: Your Google Client Secret
- Sites: Select your site

### **Error: "Client ID not found"**

**Fix:** Check your `.env` file has:
```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

And restart your server:
```bash
python manage.py runserver
```

### **Users Can't Sign In**

**Check:**
1. Google OAuth app is enabled
2. Redirect URIs are correct
3. Social Application is configured in admin
4. Site domain matches your current domain
5. `.env` variables are loaded

---

## 📈 ANALYTICS

Track Google Sign-ins:

```python
# In your view or signal
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver

@receiver(social_account_added)
def log_social_signup(request, sociallogin, **kwargs):
    if sociallogin.account.provider == 'google':
        # Log to analytics
        print(f"New Google signup: {sociallogin.account.extra_data['email']}")
```

---

## ✅ VERIFICATION CHECKLIST

After setup, verify:

- [ ] Dependencies installed: `pip list | grep allauth`
- [ ] Migrations run: `python manage.py showmigrations`
- [ ] Site configured in admin
- [ ] Social Application configured in admin
- [ ] `.env` has Google credentials
- [ ] Google Cloud Console has correct redirect URIs
- [ ] Test login works: http://localhost:8000/accounts/login/
- [ ] User created with correct user_type
- [ ] Email populated from Google
- [ ] Name populated from Google

---

## 🎉 SUCCESS!

Your Mushanai platform now supports:

✅ **Google Sign In** - One-click authentication  
✅ **Auto Account Creation** - No manual signup needed  
✅ **Account Linking** - Links to existing accounts  
✅ **Profile Auto-fill** - Gets data from Google  
✅ **Email Verified** - Trusts Google verification  
✅ **Secure** - Industry-standard OAuth 2.0  
✅ **Modern UI** - Beautiful login/signup pages  
✅ **Production Ready** - Works with SSL/HTTPS  

---

## 📚 RESOURCES

### **Documentation:**
- Django-allauth: https://django-allauth.readthedocs.io/
- Google OAuth: https://developers.google.com/identity/protocols/oauth2
- Google Cloud Console: https://console.cloud.google.com/

### **Examples:**
- Login: http://localhost:8000/accounts/login/
- Signup: http://localhost:8000/accounts/signup/
- Logout: http://localhost:8000/accounts/logout/

### **Files Modified:**
- `requirements.txt` - Added packages
- `mushanaicore/settings.py` - Allauth configuration
- `mushanaicore/urls.py` - Added allauth URLs
- `accounts/adapters.py` - Custom logic
- `templates/account/*.html` - UI templates

---

## 🚀 NEXT STEPS

### **Optional Enhancements:**

1. **Add Facebook Login:**
   - Follow similar steps for Facebook OAuth
   - Add provider to settings
   
2. **Add Profile Pictures:**
   - Fetch profile photo from Google
   - Save to user profile

3. **Two-Factor Authentication:**
   - Add `django-allauth-2fa`
   - Extra security layer

4. **Social Sharing:**
   - Let users share products on Google
   - Integration with Google Analytics

5. **Advanced Features:**
   - Remember device
   - Trusted browsers
   - Login notifications
   - Activity log

---

**🔐 Your users can now sign in with Google!**  
**🎉 One-click authentication is live!**  
**🚀 Modern, secure, and user-friendly!**  

**Setup Time:** ~10 minutes  
**User Experience:** 1-click sign in  
**Security:** ✅ Industry standard  
**Documentation:** ✅ Complete  

🌟 **Welcome to modern authentication!** 🌟

