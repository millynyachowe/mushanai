"""
Social Media Posting Services

Handles posting to Facebook, Instagram, and other platforms
"""
import requests
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class SocialMediaService:
    """Base class for social media services"""
    
    def __init__(self, social_account):
        self.social_account = social_account
        self.access_token = social_account.access_token
    
    def post_product(self, product, post_text, image_url=None):
        """Post a product to social media"""
        raise NotImplementedError("Subclasses must implement post_product")
    
    def delete_post(self, post_id):
        """Delete a post"""
        raise NotImplementedError("Subclasses must implement delete_post")
    
    def get_post_metrics(self, post_id):
        """Get engagement metrics for a post"""
        raise NotImplementedError("Subclasses must implement get_post_metrics")


class FacebookService(SocialMediaService):
    """Facebook posting service"""
    
    BASE_URL = 'https://graph.facebook.com/v18.0'
    
    def post_product(self, product, post_text, image_url=None):
        """
        Post a product to Facebook Page
        
        Returns: (success: bool, post_id: str, error: str)
        """
        try:
            # Get page access token
            page_id = self.social_account.account_id
            
            # Prepare post data
            url = f"{self.BASE_URL}/{page_id}/feed"
            
            params = {
                'access_token': self.access_token,
                'message': post_text,
            }
            
            # Add link to product
            if hasattr(settings, 'SITE_URL'):
                product_url = f"{settings.SITE_URL}/products/{product.slug}/"
                params['link'] = product_url
            
            # Post
            response = requests.post(url, data=params, timeout=30)
            data = response.json()
            
            if response.status_code == 200 and 'id' in data:
                return True, data['id'], None
            else:
                error = data.get('error', {}).get('message', 'Unknown error')
                return False, None, error
                
        except Exception as e:
            return False, None, str(e)
    
    def post_product_with_photo(self, product, post_text, image_path):
        """
        Post a product with photo to Facebook Page
        
        Args:
            product: Product instance
            post_text: Post caption
            image_path: Full path to image file
        
        Returns: (success: bool, post_id: str, error: str)
        """
        try:
            page_id = self.social_account.account_id
            url = f"{self.BASE_URL}/{page_id}/photos"
            
            params = {
                'access_token': self.access_token,
                'caption': post_text,
            }
            
            # Add product link
            if hasattr(settings, 'SITE_URL'):
                product_url = f"{settings.SITE_URL}/products/{product.slug}/"
                params['link'] = product_url
            
            # Open and send image
            with open(image_path, 'rb') as image_file:
                files = {'source': image_file}
                response = requests.post(url, data=params, files=files, timeout=60)
            
            data = response.json()
            
            if response.status_code == 200 and 'id' in data:
                return True, data['id'], None
            else:
                error = data.get('error', {}).get('message', 'Unknown error')
                return False, None, error
                
        except Exception as e:
            return False, None, str(e)
    
    def delete_post(self, post_id):
        """Delete a Facebook post"""
        try:
            url = f"{self.BASE_URL}/{post_id}"
            params = {'access_token': self.access_token}
            
            response = requests.delete(url, params=params, timeout=30)
            return response.status_code == 200
            
        except Exception as e:
            return False
    
    def get_post_metrics(self, post_id):
        """
        Get engagement metrics for a post
        
        Returns: dict with likes, comments, shares, reach
        """
        try:
            url = f"{self.BASE_URL}/{post_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'likes.summary(true),comments.summary(true),shares'
            }
            
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            return {
                'likes': data.get('likes', {}).get('summary', {}).get('total_count', 0),
                'comments': data.get('comments', {}).get('summary', {}).get('total_count', 0),
                'shares': data.get('shares', {}).get('count', 0),
                'reach': 0,  # Requires insights API
            }
            
        except Exception as e:
            return {'likes': 0, 'comments': 0, 'shares': 0, 'reach': 0}


class InstagramService(SocialMediaService):
    """Instagram posting service (via Facebook Graph API)"""
    
    BASE_URL = 'https://graph.facebook.com/v18.0'
    
    def post_product(self, product, post_text, image_url):
        """
        Post a product to Instagram Business Account
        
        Instagram requires a 2-step process:
        1. Create media container
        2. Publish the container
        
        Args:
            product: Product instance
            post_text: Post caption
            image_url: Publicly accessible image URL
        
        Returns: (success: bool, post_id: str, error: str)
        """
        try:
            instagram_account_id = self.social_account.account_id
            
            # Step 1: Create media container
            create_url = f"{self.BASE_URL}/{instagram_account_id}/media"
            create_params = {
                'access_token': self.access_token,
                'image_url': image_url,
                'caption': post_text,
            }
            
            response = requests.post(create_url, data=create_params, timeout=30)
            data = response.json()
            
            if response.status_code != 200 or 'id' not in data:
                error = data.get('error', {}).get('message', 'Failed to create media container')
                return False, None, error
            
            container_id = data['id']
            
            # Step 2: Publish the container
            publish_url = f"{self.BASE_URL}/{instagram_account_id}/media_publish"
            publish_params = {
                'access_token': self.access_token,
                'creation_id': container_id,
            }
            
            response = requests.post(publish_url, data=publish_params, timeout=30)
            data = response.json()
            
            if response.status_code == 200 and 'id' in data:
                return True, data['id'], None
            else:
                error = data.get('error', {}).get('message', 'Failed to publish')
                return False, None, error
                
        except Exception as e:
            return False, None, str(e)
    
    def delete_post(self, post_id):
        """Delete an Instagram post"""
        try:
            url = f"{self.BASE_URL}/{post_id}"
            params = {'access_token': self.access_token}
            
            response = requests.delete(url, params=params, timeout=30)
            return response.status_code == 200
            
        except Exception as e:
            return False
    
    def get_post_metrics(self, post_id):
        """Get engagement metrics for Instagram post"""
        try:
            url = f"{self.BASE_URL}/{post_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'like_count,comments_count,engagement'
            }
            
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            return {
                'likes': data.get('like_count', 0),
                'comments': data.get('comments_count', 0),
                'shares': 0,  # Instagram doesn't provide shares
                'reach': 0,  # Requires insights API
            }
            
        except Exception as e:
            return {'likes': 0, 'comments': 0, 'shares': 0, 'reach': 0}


class SocialMediaPoster:
    """Main class for posting to social media"""
    
    @staticmethod
    def get_service(social_account):
        """Get the appropriate service for a social media account"""
        if social_account.platform == 'FACEBOOK':
            return FacebookService(social_account)
        elif social_account.platform == 'INSTAGRAM':
            return InstagramService(social_account)
        else:
            raise ValueError(f"Unsupported platform: {social_account.platform}")
    
    @staticmethod
    def post_product(product, social_account, post_text=None, image_path=None):
        """
        Post a product to a social media account
        
        Args:
            product: Product instance
            social_account: SocialMediaAccount instance
            post_text: Optional custom post text (uses template if not provided)
            image_path: Optional path to image file
        
        Returns: ProductSocialPost instance
        """
        from .models import ProductSocialPost, SocialMediaTemplate
        
        # Get or generate post text
        if not post_text:
            # Try to get default template
            template = SocialMediaTemplate.objects.filter(
                vendor=product.vendor,
                platform=social_account.platform,
                is_default=True
            ).first()
            
            if template:
                post_text = template.render(product)
            else:
                # Generate default text
                post_text = f"{product.name}\n\n{product.description[:200]}\n\nPrice: ${product.price}"
                if hasattr(settings, 'SITE_URL'):
                    post_text += f"\n\n{settings.SITE_URL}/products/{product.slug}/"
        
        # Create post record
        social_post = ProductSocialPost.objects.create(
            product=product,
            vendor=product.vendor,
            social_account=social_account,
            post_text=post_text,
            status='PENDING'
        )
        
        try:
            # Get service
            service = SocialMediaPoster.get_service(social_account)
            
            # Post to platform
            if image_path and social_account.platform == 'FACEBOOK':
                success, post_id, error = service.post_product_with_photo(
                    product, post_text, image_path
                )
            elif social_account.platform == 'INSTAGRAM':
                # Instagram requires public image URL
                if hasattr(product, 'image') and product.image:
                    image_url = f"{settings.SITE_URL}{product.image.url}"
                    success, post_id, error = service.post_product(
                        product, post_text, image_url
                    )
                else:
                    success, post_id, error = False, None, "No product image available"
            else:
                success, post_id, error = service.post_product(
                    product, post_text
                )
            
            # Update post record
            if success:
                social_post.status = 'POSTED'
                social_post.post_id = post_id
                social_post.posted_at = timezone.now()
                
                # Update account stats
                social_account.total_posts += 1
                social_account.last_post_at = timezone.now()
                social_account.save()
            else:
                social_post.status = 'FAILED'
                social_post.error_message = error
            
            social_post.save()
            return social_post
            
        except Exception as e:
            social_post.status = 'FAILED'
            social_post.error_message = str(e)
            social_post.save()
            return social_post
    
    @staticmethod
    def auto_post_product(product):
        """
        Auto-post product to all accounts with auto_post enabled
        
        Args:
            product: Product instance
        
        Returns: list of ProductSocialPost instances
        """
        from .models import SocialMediaAccount
        
        # Get accounts with auto-post enabled
        accounts = SocialMediaAccount.objects.filter(
            vendor=product.vendor,
            auto_post=True,
            status='ACTIVE'
        )
        
        posts = []
        for account in accounts:
            # Get image path if available
            image_path = None
            if hasattr(product, 'image') and product.image:
                try:
                    image_path = product.image.path
                except:
                    pass
            
            # Post
            post = SocialMediaPoster.post_product(
                product, account, image_path=image_path
            )
            posts.append(post)
        
        return posts
    
    @staticmethod
    def update_post_metrics(social_post):
        """Update engagement metrics for a post"""
        if social_post.status != 'POSTED' or not social_post.post_id:
            return
        
        try:
            service = SocialMediaPoster.get_service(social_post.social_account)
            metrics = service.get_post_metrics(social_post.post_id)
            
            social_post.likes_count = metrics.get('likes', 0)
            social_post.comments_count = metrics.get('comments', 0)
            social_post.shares_count = metrics.get('shares', 0)
            social_post.reach = metrics.get('reach', 0)
            social_post.save()
            
        except Exception as e:
            pass  # Silently fail

