# Product Recommendations Engine Implementation

## ✅ Completed Features

### 1. Product View Tracking
- **ProductView Model**: Tracks individual product views with timestamps
- **View Count**: Products track total view count
- **Customer/Session Tracking**: Tracks views for both authenticated customers and anonymous sessions
- **IP Address Tracking**: Optional IP address tracking for analytics
- **Admin Interface**: ProductViewAdmin for viewing analytics

### 2. "Customers Who Bought This Also Bought"
- **Algorithm**: Based on order history - finds products bought by customers who purchased the current product
- **Purchase Frequency**: Orders by purchase frequency (most commonly bought together)
- **Implementation**: `get_customers_also_bought()` function
- **Display**: Shown on product detail pages

### 3. Similar Products
- **Algorithm**: Based on category, brand, vendor, and attributes (local materials)
- **Priority**: Same category > same brand > same vendor > same attributes
- **Rating Integration**: Orders by average rating, review count, and sales
- **Implementation**: `get_similar_products()` function
- **Display**: Shown on product detail pages

### 4. Recently Viewed Products
- **Tracking**: Automatically tracks product views when viewing product detail page
- **Customer Dashboard**: Updates customer dashboard's recently viewed products list
- **Session Support**: Works for both authenticated customers and anonymous sessions
- **Limit**: Keeps last 20 viewed products
- **Implementation**: `get_recently_viewed()` function
- **Display**: Shown on product detail pages and customer portal

### 5. Personalized Recommendations
- **Algorithm**: Based on customer's purchase history
- **Category Matching**: Recommends products from categories customer has purchased from
- **Brand Matching**: Recommends products from brands customer has purchased from
- **Exclusion**: Excludes products customer has already purchased
- **Fallback**: If no purchase history, shows trending products
- **Implementation**: `get_personalized_recommendations()` function
- **Display**: Shown on customer portal

### 6. Seasonal/Trending Product Suggestions
- **Trending Algorithm**: Based on recent views, sales, and reviews (last 30 days)
- **Featured Products**: Prioritizes featured products
- **Activity Metrics**: Considers recent sales, views, and review counts
- **Implementation**: `get_trending_products()` and `get_seasonal_suggestions()` functions
- **Display**: Shown on homepage and customer portal

## 📁 Files Created/Modified

### Models
- `products/models.py`: 
  - Added `view_count` field to Product
  - Added `ProductView` model for tracking views

### Recommendation Engine
- `products/recommendations.py`: 
  - `get_customers_also_bought()`: Customers who bought this also bought
  - `get_similar_products()`: Similar products based on attributes
  - `get_recently_viewed()`: Recently viewed products
  - `get_personalized_recommendations()`: Personalized recommendations
  - `get_trending_products()`: Trending products
  - `get_seasonal_suggestions()`: Seasonal/trending suggestions
  - `track_product_view()`: Track product views

### Views
- `store/views.py`: 
  - Updated `home()`: Added seasonal products
  - Added `product_detail()`: Product detail page with recommendations
- `customers/views.py`: 
  - Updated `customer_portal()`: Added personalized recommendations, recently viewed, trending, and seasonal products

### Templates
- `templates/store/product_detail.html`: Product detail page with recommendations
- `templates/store/index.html`: Added trending products section and product links
- `templates/customers/portal.html`: Added recommendation sections
- `templates/store/search.html`: Added product detail links

### Admin
- `products/admin.py`: 
  - Added `ProductViewAdmin` for viewing product view analytics
  - Updated `ProductAdmin` to show `view_count`

### URLs
- `store/urls.py`: Added product detail route

### Migrations
- `products/migrations/0003_product_view_count_productview.py`: Migration for ProductView model

## 🎯 Features

### Product Detail Page
1. **Product Information**: Full product details, images, reviews
2. **Customers Also Bought**: Shows products frequently bought together
3. **Similar Products**: Shows similar products based on category/brand/vendor
4. **Recently Viewed**: Shows recently viewed products (for authenticated users)
5. **View Tracking**: Automatically tracks views when page is loaded

### Customer Portal
1. **Personalized Recommendations**: Based on purchase history
2. **Recently Viewed**: Quick access to recently viewed products
3. **Trending Products**: Currently trending products
4. **Seasonal Suggestions**: Featured and trending products

### Homepage
1. **Trending Now Section**: Shows trending/seasonal products
2. **Product Links**: All products link to detail pages
3. **View Tracking**: Tracks views when products are clicked

## 🔧 Implementation Details

### View Tracking
- Views are tracked automatically when a product detail page is viewed
- Tracks customer (if authenticated) or session key (if anonymous)
- Updates product view count
- Updates customer dashboard's recently viewed products list
- Stores IP address for analytics

### Recommendation Algorithms

#### Customers Also Bought
1. Find customers who bought the current product
2. Find other products bought by those customers
3. Order by purchase frequency
4. Exclude the current product

#### Similar Products
1. Filter products by same category, brand, or vendor
2. Annotate with ratings and sales counts
3. Order by ratings, review count, and sales
4. Fallback to category or vendor if no matches

#### Personalized Recommendations
1. Get customer's purchase history
2. Extract categories and brands from purchases
3. Find products in same categories/brands
4. Exclude already purchased products
5. Order by ratings and sales
6. Fallback to trending if no purchase history

#### Trending Products
1. Filter products by recent activity (last 30 days)
2. Count recent views, sales, and reviews
3. Order by activity metrics
4. Consider ratings and review counts

## 📊 Database Changes

### New Tables
- `products_productview`: Stores product view tracking data

### Updated Tables
- `products_product`: Added `view_count` field

### New Indexes
- Index on `products_productview` (product, viewed_at)
- Index on `products_productview` (customer, viewed_at)
- Index on `products_productview` (session_key, viewed_at)

## 🧪 Testing

### Manual Testing Steps

1. **View Tracking**:
   - Visit a product detail page
   - Check that view is tracked in admin
   - Verify view count is incremented

2. **Customers Also Bought**:
   - Create orders with multiple products
   - View a product detail page
   - Verify "Customers Also Bought" section shows related products

3. **Similar Products**:
   - View a product detail page
   - Verify "Similar Products" section shows products from same category/brand

4. **Recently Viewed**:
   - View multiple products as a logged-in customer
   - Check customer portal
   - Verify "Recently Viewed" section shows viewed products

5. **Personalized Recommendations**:
   - Make purchases as a customer
   - Check customer portal
   - Verify "Recommended for You" shows products from purchased categories

6. **Trending Products**:
   - View products, create orders, add reviews
   - Check trending page or homepage
   - Verify trending products are shown

## 🚀 Next Steps

### Potential Enhancements
1. **Machine Learning**: Implement ML-based recommendations
2. **Collaborative Filtering**: Enhanced collaborative filtering algorithm
3. **A/B Testing**: Test different recommendation algorithms
4. **Performance Optimization**: Cache recommendations for better performance
5. **Real-time Updates**: Update recommendations in real-time
6. **Recommendation Analytics**: Track recommendation click-through rates
7. **Personalization Engine**: More advanced personalization based on browsing behavior
8. **Seasonal Logic**: Actual seasonal product detection based on dates
9. **Recommendation Explanations**: Show why products are recommended
10. **Wishlist Integration**: Consider wishlist items in recommendations

## 🐛 Known Issues

None currently identified. All tests pass.

## 📝 Notes

- View tracking happens automatically on product detail page load
- Recommendations are calculated on-the-fly (consider caching for production)
- Personalized recommendations require purchase history
- Trending products consider last 30 days of activity
- Similar products prioritize category matches over brand matches
- All recommendations exclude inactive products
- Product views are tracked for both authenticated and anonymous users

## 💡 Usage Examples

### Get Customers Also Bought
```python
from products.recommendations import get_customers_also_bought

product = Product.objects.get(slug='example-product')
also_bought = get_customers_also_bought(product, limit=8)
```

### Get Similar Products
```python
from products.recommendations import get_similar_products

product = Product.objects.get(slug='example-product')
similar = get_similar_products(product, limit=8)
```

### Get Personalized Recommendations
```python
from products.recommendations import get_personalized_recommendations

customer = request.user
recommendations = get_personalized_recommendations(customer, limit=12)
```

### Track Product View
```python
from products.recommendations import track_product_view

track_product_view(
    product=product,
    customer=request.user if request.user.is_authenticated else None,
    session_key=request.session.session_key,
    ip_address=request.META.get('REMOTE_ADDR')
)
```

