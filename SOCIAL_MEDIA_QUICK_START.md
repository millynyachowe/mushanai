# 📱 Social Media Integration - Quick Start

## ✅ What's Ready NOW

- ✅ All database models created
- ✅ Admin interface configured
- ✅ Facebook posting service
- ✅ Instagram posting service
- ✅ Template system
- ✅ Analytics tracking
- ✅ Migrations applied

## 🚀 Quick Test (10 Minutes)

### Step 1: Create a Test Account (Manual)

For testing, you can manually create a social media account:

```bash
python manage.py shell
```

```python
from social_media.models import SocialMediaAccount
from accounts.models import User

# Get a vendor
vendor = User.objects.filter(user_type='VENDOR').first()

# Create Facebook account (with test token)
account = SocialMediaAccount.objects.create(
    vendor=vendor,
    platform='FACEBOOK',
    account_name='Test Page',
    account_id='YOUR_PAGE_ID',  # Get from Facebook
    access_token='YOUR_PAGE_ACCESS_TOKEN',  # Get from Graph API Explorer
    status='ACTIVE',
    auto_post=False
)

print(f"✅ Created: {account}")
exit()
```

### Step 2: Create a Post Template

```bash
python manage.py shell
```

```python
from social_media.models import SocialMediaTemplate
from accounts.models import User

vendor = User.objects.filter(user_type='VENDOR').first()

template = SocialMediaTemplate.objects.create(
    vendor=vendor,
    platform='FACEBOOK',
    name='Default Facebook Template',
    template_text="""🎨 New Product Alert! 🎨

{product_name}

{description}

💰 Price: {price}
🌍 Made in Zimbabwe

Shop now: {url}""",
    hashtags='ZimbabweanCrafts,Handmade,SupportLocal',
    is_default=True
)

print(f"✅ Template created: {template}")
exit()
```

### Step 3: Test Posting

```bash
python manage.py shell
```

```python
from social_media.models import SocialMediaAccount
from products.models import Product
from social_media.services import SocialMediaPoster

# Get account and product
account = SocialMediaAccount.objects.first()
product = Product.objects.first()

# Post
result = SocialMediaPoster.post_product(product, account)

print(f"Status: {result.status}")
if result.status == 'POSTED':
    print(f"✅ Posted! ID: {result.post_id}")
    print(f"URL: {result.post_url}")
else:
    print(f"❌ Error: {result.error_message}")

exit()
```

## 🔑 Getting Facebook Access Token (For Testing)

### Method 1: Graph API Explorer (Quick Test)

```
1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app (or create one)
3. Click "Get Token" → "Get Page Access Token"
4. Select your Facebook Page
5. Copy the token
6. Use this token in your test account

⚠️ This token expires in ~2 hours (for testing only!)
```

### Method 2: Long-Lived Token (For Development)

```bash
# Get user token from Graph API Explorer first, then:

curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token" \
  -d "grant_type=fb_exchange_token" \
  -d "client_id=YOUR_APP_ID" \
  -d "client_secret=YOUR_APP_SECRET" \
  -d "fb_exchange_token=SHORT_LIVED_TOKEN"

# Returns long-lived token (60 days)
```

## 📝 Example: Complete Workflow

### 1. Get Facebook Page ID

```bash
# Using Graph API Explorer:
# Query: /me/accounts
# Returns list of your pages with IDs
```

### 2. Create Account

```python
account = SocialMediaAccount.objects.create(
    vendor=vendor,
    platform='FACEBOOK',
    account_name='My Crafts Page',
    account_id='123456789',  # Your page ID
    access_token='EAAxxxxx',  # Your page token
    status='ACTIVE'
)
```

### 3. Enable Auto-Post

```python
account.auto_post = True
account.save()
```

### 4. Create Product & Auto-Post

```python
from products.models import Product

# Create product
product = Product.objects.create(
    vendor=vendor,
    name='Woven Basket',
    description='Beautiful handwoven basket',
    price=25.00,
    # ... other fields
)

# Auto-post (if auto_post enabled)
from social_media.services import SocialMediaPoster
SocialMediaPoster.auto_post_product(product)
```

## 🎨 Template Examples

### Facebook Template

```
🎨 New Product Alert! 🎨

{product_name}

{description}

💰 Price: {price}
🌍 Made in Zimbabwe
✨ Handcrafted with love

Shop now: {url}

Support local artisans!

#ZimbabweanCrafts #Handmade #SupportLocal #AfricanArt
```

### Instagram Template

```
✨ {product_name} ✨

{description}

💰 {price}
🇿🇼 Proudly Zimbabwean
♻️ Sustainably made

🔗 Link in bio!

#ZimbabweanCrafts #Handmade #AfricanDesign #EthicalFashion #SupportLocal #MadeInZimbabwe
```

## 📊 Check Posted Content

### View in Admin

```
1. Go to /admin/social_media/productsocialpost/
2. See all posted products
3. Check status, engagement metrics
```

### Via Code

```python
from social_media.models import ProductSocialPost

# Get recent posts
posts = ProductSocialPost.objects.filter(
    vendor=vendor,
    status='POSTED'
).order_by('-posted_at')[:5]

for post in posts:
    print(f"{post.product.name} → {post.social_account.platform}")
    print(f"  Likes: {post.likes_count}")
    print(f"  Comments: {post.comments_count}")
    print(f"  URL: {post.post_url}")
    print()
```

## 🔄 Update Engagement Metrics

```python
from social_media.models import ProductSocialPost
from social_media.services import SocialMediaPoster

# Update a specific post
post = ProductSocialPost.objects.filter(status='POSTED').first()
SocialMediaPoster.update_post_metrics(post)

print(f"Updated: {post.likes_count} likes, {post.comments_count} comments")
```

## 📈 View Analytics

```python
from social_media.models import ProductSocialPost
from django.db.models import Sum

posts = ProductSocialPost.objects.filter(
    vendor=vendor,
    status='POSTED'
)

stats = {
    'total_posts': posts.count(),
    'total_likes': posts.aggregate(Sum('likes_count'))['likes_count__sum'] or 0,
    'total_comments': posts.aggregate(Sum('comments_count'))['comments_count__sum'] or 0,
    'total_reach': posts.aggregate(Sum('reach'))['reach__sum'] or 0,
}

print("📊 Social Media Stats:")
print(f"  Posts: {stats['total_posts']}")
print(f"  Likes: {stats['total_likes']}")
print(f"  Comments: {stats['total_comments']}")
print(f"  Reach: {stats['total_reach']}")
```

## 🐛 Troubleshooting

### Error: "Invalid OAuth Token"

```bash
# Token expired or invalid
# Solution: Get new token from Graph API Explorer
```

### Error: "Permission Denied"

```bash
# App doesn't have required permissions
# Solution: Add permissions in Facebook App settings:
#  - pages_manage_posts
#  - pages_read_engagement
```

### Error: "Image URL not accessible" (Instagram)

```bash
# Instagram requires public image URL
# Solution: Ensure product images are publicly accessible
# Check MEDIA_URL in settings.py is accessible externally
```

### Post Shows as "FAILED"

```python
# Check error message
post = ProductSocialPost.objects.filter(status='FAILED').last()
print(f"Error: {post.error_message}")

# Common fixes:
# 1. Refresh access token
# 2. Check image URL
# 3. Verify account status
```

## 🎯 Next Steps

### 1. Get Production Tokens

```
1. Create Facebook App at developers.facebook.com
2. Configure OAuth settings
3. Implement OAuth flow (see main guide)
4. Get long-lived tokens
```

### 2. Build Frontend

```
Templates needed:
- social_media/dashboard.html
- social_media/connect_account.html
- social_media/templates_list.html
- social_media/posts_list.html
- social_media/analytics.html

Estimated: 2-3 days
```

### 3. Integrate with Product Form

```
Add to product creation/edit:
- Checkbox: "Post to social media"
- Account selection
- Custom text field
- Preview button

Estimated: 1 day
```

## 📚 Key URLs

### Admin

```
Accounts: /admin/social_media/socialmediaaccount/
Posts: /admin/social_media/productsocialpost/
Templates: /admin/social_media/socialmediatemplate/
Analytics: /admin/social_media/socialmediaanalytics/
```

### API Endpoints (When Frontend Built)

```
Dashboard: /social-media/
Connect: /social-media/connect/<platform>/
Templates: /social-media/templates/
Posts: /social-media/posts/
Analytics: /social-media/analytics/
```

## 💡 Tips

### Best Practices

```
✅ DO:
- Use high-quality product images
- Post during peak hours (1-3 PM)
- Include call-to-action
- Use 3-5 relevant hashtags (Facebook)
- Use 20-30 hashtags (Instagram)
- Track engagement metrics

❌ DON'T:
- Post too frequently (max 2-3/day)
- Use clickbait
- Forget product links
- Ignore engagement
- Use expired tokens
```

### Rate Limits

```
Facebook: ~200 calls/hour
Instagram: ~200 calls/hour

Implement rate limiting in production!
```

## ✅ Checklist

### To Go Live:

- [ ] Create Facebook App
- [ ] Configure OAuth
- [ ] Get production tokens
- [ ] Test posting to real accounts
- [ ] Build frontend templates
- [ ] Integrate with product form
- [ ] Set up token refresh logic
- [ ] Implement rate limiting
- [ ] Add error handling
- [ ] Train vendors on usage

---

**Status:** ✅ Backend Complete  
**Time to Production:** 4-6 days (with OAuth & Frontend)  
**Documentation:** SOCIAL_MEDIA_INTEGRATION_GUIDE.md  
**Last Updated:** November 19, 2025

🎉 **Ready to help vendors reach more customers!** 📱✨

