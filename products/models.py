from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

User = get_user_model()


class Category(models.Model):
    """
    Product categories
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    # Display customization
    display_header = models.CharField(max_length=200, blank=True, null=True, help_text='Custom header for homepage (e.g., "Premium Picks")')
    display_tagline = models.CharField(max_length=300, blank=True, null=True, help_text='Tagline for homepage (e.g., "Exquisite Creations, Made Locally")')
    
    # Tier classification
    TIER_CHOICES = [
        ('PREMIUM', 'Premium/Luxury'),
        ('MID_TIER', 'Mid-tier'),
        ('AFFORDABLE', 'Affordable/Everyday'),
    ]
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='MID_TIER', help_text='Category tier for segmentation')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['tier', 'name']
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    """
    Local brands managed by vendors
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_local = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Products sold on the platform
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True, null=True)
    
    # Relationships
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        limit_choices_to={'user_type': 'VENDOR'},
        null=True,
        blank=True
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', help_text='Required: Select the primary category for this product')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    tags = models.ManyToManyField('ProductTag', related_name='products', blank=True, help_text='Optional: Add tags to help customers find this product')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    
    # Inventory
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    track_inventory = models.BooleanField(default=True)
    
    # Offline vendor details (for admin-managed local brands)
    offline_vendor_name = models.CharField(max_length=200, blank=True, null=True)
    offline_vendor_phone = models.CharField(max_length=50, blank=True, null=True)
    offline_vendor_address = models.TextField(blank=True, null=True)
    
    # Display
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_made_from_local_materials = models.BooleanField(default=False)
    
    # Images
    primary_image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Search tracking
    search_count = models.PositiveIntegerField(default=0)
    unavailable_requests = models.PositiveIntegerField(default=0)  # Track when product is searched but unavailable
    
    # View tracking
    view_count = models.PositiveIntegerField(default=0)  # Total view count
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_featured', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['vendor', 'is_active']),
            models.Index(fields=['price', 'is_active']),
            models.Index(fields=['is_made_from_local_materials', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def has_vendor_account(self):
        return self.vendor is not None
    
    @property
    def vendor_display_name(self):
        if self.vendor:
            return self.vendor.get_full_name() or self.vendor.username
        if self.offline_vendor_name:
            return self.offline_vendor_name
        return "Local Vendor"
    
    @property
    def vendor_contact_phone(self):
        if self.vendor:
            return getattr(self.vendor, 'phone_number', None)
        return self.offline_vendor_phone
    
    @property
    def vendor_contact_address(self):
        if self.vendor and hasattr(self.vendor, 'profile'):
            return getattr(self.vendor.profile, 'address', None)
        return self.offline_vendor_address
    
    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        rating = self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(rating, 1) if rating else 0.0
    
    @property
    def review_count(self):
        """Get total number of reviews"""
        return self.reviews.count()
    
    @property
    def popularity_score(self):
        """Calculate popularity based on search count, reviews, and sales"""
        from orders.models import OrderItem
        sales_count = OrderItem.objects.filter(product=self).count()
        return self.search_count + (self.review_count * 2) + sales_count
    
    def clean(self):
        """Validate product data"""
        super().clean()
        if not self.vendor and not self.offline_vendor_name:
            raise ValidationError('Either vendor or offline_vendor_name must be provided.')
        if not self.category:
            raise ValidationError('Category is required for all products.')
    
    def customer_has_purchased(self, customer):
        """Check if customer has purchased this product"""
        from orders.models import OrderItem
        return OrderItem.objects.filter(
            order__customer=customer,
            product=self,
            order__payment_status='PAID'
        ).exists()


class ProductImage(models.Model):
    """
    Additional images for products
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"


class ProductReview(models.Model):
    """
    Product reviews and ratings
    """
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews', limit_choices_to={'user_type': 'CUSTOMER'})
    rating = models.IntegerField(choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True, null=True)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  # Admin moderation
    
    # Vendor response
    vendor_response = models.TextField(blank=True, null=True)
    vendor_response_date = models.DateTimeField(blank=True, null=True)
    
    # Helpful votes
    helpful_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'customer']  # One review per customer per product
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'rating']),
            models.Index(fields=['is_approved', 'created_at']),
            models.Index(fields=['is_verified_purchase', 'is_approved']),
        ]
    
    def __str__(self):
        return f"{self.customer.username} - {self.product.name} - {self.rating} stars"
    
    def save(self, *args, **kwargs):
        # Auto-set verified purchase if customer has purchased the product
        if not self.is_verified_purchase and self.customer and self.product:
            self.is_verified_purchase = self.product.customer_has_purchased(self.customer)
        super().save(*args, **kwargs)

    def clean(self):
        """Validate review data"""
        super().clean()


class ReviewPhoto(models.Model):
    """
    Photos attached to product reviews
    """
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='reviews/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Photo for {self.review.product.name} review by {self.review.customer.username}"


class ReviewHelpfulVote(models.Model):
    """
    Track helpful votes on reviews
    """
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='helpful_votes')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_helpful_votes', limit_choices_to={'user_type': 'CUSTOMER'}, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)  # For anonymous users
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['review', 'customer'], ['review', 'session_key']]
        indexes = [
            models.Index(fields=['review', 'customer']),
            models.Index(fields=['review', 'session_key']),
        ]
    
    def __str__(self):
        user = self.customer.username if self.customer else 'Anonymous'
        return f"{user} found {self.review} helpful"


class ProductView(models.Model):
    """
    Track individual product views for recommendations
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_views', limit_choices_to={'user_type': 'CUSTOMER'}, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)  # For anonymous users
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['product', 'viewed_at']),
            models.Index(fields=['customer', 'viewed_at']),
            models.Index(fields=['session_key', 'viewed_at']),
        ]
    
    def __str__(self):
        user = self.customer.username if self.customer else 'Anonymous'
        return f"{user} viewed {self.product.name} at {self.viewed_at}"


class ProductTag(models.Model):
    """
    Tags for products (created by admin, used by vendors)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=20, default='#be8400', help_text='Color for tag display')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CategoryDisplaySchedule(models.Model):
    """
    Admin can schedule which categories to display on homepage
    """
    PERIOD_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='display_schedules')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True, help_text='Leave blank for ongoing display')
    display_order = models.PositiveIntegerField(default=0, help_text='Order on homepage (lower = first)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'category__name']
        unique_together = [['category', 'period', 'start_date']]
    
    def __str__(self):
        return f"{self.category.name} - {self.get_period_display()} ({self.start_date})"
    
    def is_current(self):
        """Check if schedule is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        if not self.is_active:
            return False
        if self.start_date > today:
            return False
        if self.end_date and self.end_date < today:
            return False
        return True
