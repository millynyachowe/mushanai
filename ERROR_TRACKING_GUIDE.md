# 🚨 Error Tracking & Monitoring - Complete Guide

## 📊 Overview

Your Mushanai platform now has **professional error tracking** with Sentry and performance profiling!

### **What Was Added:**

✅ **Sentry Integration** - Real-time error tracking  
✅ **Performance Monitoring** - Track slow requests  
✅ **Custom Error Pages** - Beautiful 400/403/404/500 pages  
✅ **Django Silk** - Local performance profiling  
✅ **Error Notifications** - Get alerted on critical issues  
✅ **Breadcrumbs** - Track user actions before errors  

---

## 🎯 Why This Matters

### **Before Error Tracking:**
❌ Users encounter errors silently  
❌ You don't know what's breaking  
❌ No visibility into performance issues  
❌ Debugging is guesswork  
❌ Production bugs go unnoticed  

### **After Error Tracking:**
✅ Instant error notifications  
✅ Full stack traces  
✅ User context (who/where/when)  
✅ Performance insights  
✅ Proactive bug fixing  

---

## 🚀 Quick Setup

### **1. Sign Up for Sentry (Free)**

1. Go to [sentry.io](https://sentry.io/)
2. Create free account
3. Create new project → Select "Django"
4. Copy your DSN (looks like: `https://xxxxx@o123456.ingest.sentry.io/123456`)

### **2. Update .env File**

```bash
# Add to .env file
SENTRY_DSN=https://your_actual_dsn_here@o123456.ingest.sentry.io/123456
SENTRY_ENVIRONMENT=production  # or development/staging
SENTRY_RELEASE=v1.0.0  # Optional: track releases
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Test It Works**

```bash
# Start server
python manage.py runserver

# Trigger test error
python manage.py shell
>>> import sentry_sdk
>>> sentry_sdk.capture_message("Test message from Django!")

# Check Sentry dashboard - you should see the message!
```

---

## 🎨 Features

### **1. Automatic Error Capture**

**All errors are automatically captured:**
- Unhandled exceptions
- Database errors
- Template errors
- View errors
- 500 errors

**Example:**
```python
def my_view(request):
    # This error will be automatically captured by Sentry
    result = 1 / 0  # ZeroDivisionError
```

### **2. Custom Error Messages**

```python
from sentry_sdk import capture_message, capture_exception

# Capture custom message
capture_message("User attempted unauthorized action", level="warning")

# Capture specific exception
try:
    process_payment()
except Exception as e:
    capture_exception(e)
    # Handle gracefully
```

### **3. User Context**

Sentry automatically captures:
- User ID
- Username
- Email
- IP address
- Browser/device
- URL path

### **4. Custom Context**

```python
from sentry_sdk import configure_scope

def checkout_view(request):
    with configure_scope() as scope:
        scope.set_context("order", {
            "order_id": order.id,
            "total": str(order.total),
            "items_count": order.items.count()
        })
        
        # Process order
        # Any errors will include this context
```

### **5. Breadcrumbs**

Track user actions before an error:

```python
from sentry_sdk import add_breadcrumb

# Track user actions
add_breadcrumb(
    category='user_action',
    message='User added item to cart',
    level='info',
    data={'product_id': product.id}
)

# Automatic breadcrumbs for:
# - HTTP requests
# - Database queries
# - Cache operations
# - Logging calls
```

### **6. Performance Monitoring**

Tracks:
- Page load times
- Database query performance
- Cache hit rates
- External API calls
- Template rendering

**View in Sentry Dashboard:**
- Slowest endpoints
- Most frequent queries
- Performance trends
- N+1 query detection

---

## 🎭 Custom Error Pages

Beautiful, branded error pages for:

### **404 - Not Found**
- Purple gradient
- Clear message
- "Go Home" button
- User-friendly

### **500 - Server Error**
- Red gradient
- Reassuring message
- Error automatically sent to Sentry
- "We've been notified" message

### **403 - Forbidden**
- Orange gradient
- Permission denial message
- Clear call-to-action

### **400 - Bad Request**
- Blue gradient
- Helpful error message
- Recovery options

**Features:**
- Responsive design
- Modern UI
- Consistent branding
- Mobile-friendly
- Fast loading

---

## 🔍 Django Silk (Development Only)

**Performance profiling tool for local development.**

### **Access Silk:**

```bash
http://localhost:8000/silk/
```

### **Features:**

1. **Request Profiling**
   - See all HTTP requests
   - Response times
   - SQL queries
   - View parameters

2. **SQL Analysis**
   - Query count
   - Execution time
   - Duplicate queries
   - N+1 detection

3. **Python Profiling**
   - Function call trees
   - Execution time
   - Memory usage
   - Bottleneck identification

4. **Comparison Tool**
   - Compare requests
   - Before/after optimization
   - Performance regression

### **Usage:**

```python
# Silk decorators
from silk.profiling.profiler import silk_profile

@silk_profile(name='Heavy Operation')
def expensive_function():
    # Your code
    pass
```

---

## 📊 Monitoring Dashboard

### **Sentry Dashboard Includes:**

1. **Issues**
   - All errors
   - Frequency
   - Last seen
   - Affected users
   - Stack traces

2. **Performance**
   - Transaction traces
   - Slow endpoints
   - Query performance
   - Web vitals

3. **Releases**
   - Track deployments
   - Error rates per release
   - Regression detection

4. **Alerts**
   - Email notifications
   - Slack integration
   - PagerDuty
   - Custom webhooks

---

## ⚙️ Configuration

### **Sentry Settings (settings.py)**

```python
sentry_sdk.init(
    dsn=SENTRY_DSN,
    
    # Sample rate for performance
    traces_sample_rate=1.0,  # 100% in dev, 0.1 (10%) in prod
    
    # Sample rate for profiling
    profiles_sample_rate=1.0,  # 100% in dev, 0.1 (10%) in prod
    
    # Environment
    environment='production',  # or development/staging
    
    # Release tracking
    release='v1.0.0',
    
    # Include user data
    send_default_pii=True,
    
    # Ignored errors
    ignore_errors=[
        'django.http.Http404',
        'django.exceptions.DisallowedHost',
    ],
)
```

### **Adjusting Sample Rates:**

**Development:**
```python
traces_sample_rate=1.0  # Capture all transactions
```

**Production:**
```python
traces_sample_rate=0.1  # Capture 10% (reduces cost)
```

---

## 🔔 Alert Configuration

### **1. Set Up in Sentry Dashboard:**

1. Go to **Alerts** → **Create Alert Rule**
2. Choose conditions:
   - Error rate threshold
   - New issue
   - Regression
   - Performance degradation

### **2. Alert Channels:**

- **Email** - Instant notifications
- **Slack** - Team channel alerts
- **PagerDuty** - On-call rotation
- **Webhooks** - Custom integrations

### **3. Alert Examples:**

**Critical Errors:**
```
When an error occurs more than 10 times in 1 minute
→ Send to #critical-alerts Slack channel
```

**Performance Degradation:**
```
When average response time > 1 second for 5 minutes
→ Email engineering team
```

**New Issues:**
```
When a new unique error appears
→ Send to #bugs Slack channel
```

---

## 🧪 Testing Error Tracking

### **Test 1: Capture Message**

```python
python manage.py shell

>>> import sentry_sdk
>>> sentry_sdk.capture_message("Test message from Django!")

# Check Sentry dashboard
```

### **Test 2: Capture Exception**

```python
>>> try:
...     1 / 0
... except Exception as e:
...     sentry_sdk.capture_exception(e)

# Check Sentry dashboard
```

### **Test 3: Trigger 404 Error**

```bash
# Visit non-existent page
http://localhost:8000/this-page-does-not-exist/

# Should see beautiful 404 page
```

### **Test 4: Test Custom Error Page**

Create temporary view to trigger 500:

```python
# In any views.py
def test_error(request):
    raise Exception("Test error for Sentry!")
```

Visit the URL - should see custom 500 page and error in Sentry.

---

## 📈 Best Practices

### **1. Add Context to Errors**

```python
from sentry_sdk import configure_scope

with configure_scope() as scope:
    scope.set_tag("payment_method", "stripe")
    scope.set_user({"id": user.id, "email": user.email})
    scope.set_context("order", {"id": order.id, "amount": order.total})
    
    # Your code
```

### **2. Use Breadcrumbs**

```python
from sentry_sdk import add_breadcrumb

add_breadcrumb(
    category='cart',
    message='Item added to cart',
    level='info',
    data={'product_id': product.id, 'quantity': 2}
)
```

### **3. Filter Sensitive Data**

```python
# In sentry_sdk.init()
before_send=lambda event, hint: filter_sensitive_data(event, hint)

def filter_sensitive_data(event, hint):
    # Remove sensitive info
    if 'request' in event:
        if 'headers' in event['request']:
            event['request']['headers'].pop('Authorization', None)
    return event
```

### **4. Set Release Versions**

```python
# settings.py
SENTRY_RELEASE = f"mushanai@{os.getenv('GIT_COMMIT', 'dev')}"

sentry_sdk.init(
    release=SENTRY_RELEASE
)
```

### **5. Monitor Performance**

```python
from sentry_sdk import start_transaction

with start_transaction(op="task", name="process_order"):
    # Your code
    process_payment()
    send_confirmation_email()
```

---

## 🔒 Security Considerations

### **1. Don't Track PII in Production**

```python
send_default_pii=False  # in production
```

### **2. Filter Sensitive Headers**

```python
ignore_errors=[
    'django.http.Http404',
    'KeyError',  # If contains sensitive keys
]
```

### **3. Use Environment Variables**

```bash
# Never commit Sentry DSN to git!
SENTRY_DSN=https://...  # In .env file
```

---

## 💰 Cost Optimization

### **Free Tier Limits:**
- 5,000 errors/month
- 10,000 transactions/month
- 30-day retention

### **Stay Within Free Tier:**

1. **Reduce Sample Rate:**
```python
traces_sample_rate=0.1  # Only 10% of transactions
```

2. **Filter Common Errors:**
```python
ignore_errors=['Http404', 'PermissionDenied']
```

3. **Use Filters:**
```python
before_send=lambda event, hint: event if should_send(event) else None
```

4. **Development vs Production:**
```python
if DEBUG:
    traces_sample_rate=1.0
else:
    traces_sample_rate=0.1
```

---

## 📊 Metrics to Monitor

### **1. Error Rate**
- Errors per minute
- Trends over time
- By endpoint

### **2. Performance**
- Average response time
- Slowest endpoints
- Database query time

### **3. User Impact**
- Affected users
- Error frequency per user
- Geographic distribution

### **4. Release Quality**
- Errors by release
- New issues per deployment
- Regression detection

---

## 🚀 Production Checklist

Before deploying:

- [ ] Sentry DSN configured in `.env`
- [ ] Environment set to `production`
- [ ] Sample rates adjusted (10-20%)
- [ ] Alert rules configured
- [ ] Team notifications set up
- [ ] PII filtering enabled
- [ ] Custom error pages tested
- [ ] Release tracking configured
- [ ] Sensitive data filtered
- [ ] Performance baseline established

---

## 🎉 Success!

Your platform now has:

✅ **Real-time Error Tracking**
✅ **Performance Monitoring**
✅ **Beautiful Error Pages**
✅ **User Context Capture**
✅ **Breadcrumb Tracking**
✅ **Alert Notifications**
✅ **Performance Profiling**
✅ **Release Tracking**

---

## 🔗 Resources

- **Sentry Dashboard:** [sentry.io](https://sentry.io/)
- **Sentry Docs:** [docs.sentry.io/platforms/python/guides/django](https://docs.sentry.io/platforms/python/guides/django/)
- **Django Silk:** [http://localhost:8000/silk/](http://localhost:8000/silk/) (dev only)
- **Error Pages:** `/templates/errors/`

---

## 💡 Pro Tips

1. **Set up Slack alerts** for critical errors
2. **Monitor performance trends** weekly
3. **Review Sentry dashboard** daily
4. **Tag errors** by feature/module
5. **Track releases** for easier debugging
6. **Use breadcrumbs** liberally
7. **Filter noisy errors** to reduce noise
8. **Set up custom dashboards** for your team

---

**🎊 Never miss a bug again! Your platform is now production-grade! 🚀**

