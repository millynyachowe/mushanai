"""
Management command to create default vendor badges
"""
from django.core.management.base import BaseCommand
from vendors.models import VendorBadge


class Command(BaseCommand):
    help = 'Create default vendor badges'

    def handle(self, *args, **options):
        badges_data = [
            {
                'name': 'Verified Vendor',
                'badge_type': 'VERIFIED',
                'description': 'This vendor has been verified by Mushanai administration',
                'icon': '✓',
                'color': '#be8400',
            },
            {
                'name': 'Top Seller',
                'badge_type': 'TOP_SELLER',
                'description': 'This vendor has achieved high sales volume',
                'icon': '🏆',
                'color': '#ffd700',
                'min_sales': 100,
                'min_revenue': 10000,
            },
            {
                'name': 'Local Champion',
                'badge_type': 'LOCAL_CHAMPION',
                'description': 'This vendor promotes local products and materials',
                'icon': '🇿🇼',
                'color': '#be8400',
                'min_local_products': 10,
            },
            {
                'name': 'Eco-Friendly',
                'badge_type': 'ECO_FRIENDLY',
                'description': 'This vendor offers eco-friendly and sustainable products',
                'icon': '🌱',
                'color': '#28a745',
                'min_eco_products': 5,
            },
            {
                'name': 'Fast Responder',
                'badge_type': 'FAST_RESPONDER',
                'description': 'This vendor responds to customer reviews quickly',
                'icon': '⚡',
                'color': '#17a2b8',
                'max_response_time_hours': 24,
            },
            {
                'name': 'High Rated',
                'badge_type': 'HIGH_RATED',
                'description': 'This vendor maintains high customer ratings',
                'icon': '⭐',
                'color': '#ffc107',
                'min_rating': 4.5,
                'min_reviews': 10,
            },
            {
                'name': 'Community Hero',
                'badge_type': 'COMMUNITY_HERO',
                'description': 'This vendor actively supports community projects',
                'icon': '❤️',
                'color': '#dc3545',
            },
            {
                'name': 'Trusted Vendor',
                'badge_type': 'TRUSTED_VENDOR',
                'description': 'This vendor is trusted and verified with high ratings',
                'icon': '🛡️',
                'color': '#6f42c1',
                'min_rating': 4.0,
                'min_reviews': 10,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for badge_data in badges_data:
            badge, created = VendorBadge.objects.get_or_create(
                badge_type=badge_data['badge_type'],
                defaults=badge_data
            )
            
            if not created:
                # Update existing badge
                for key, value in badge_data.items():
                    setattr(badge, key, value)
                badge.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated badge: {badge.name}'))
            else:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created badge: {badge.name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully created {created_count} badges and updated {updated_count} badges.'
        ))

