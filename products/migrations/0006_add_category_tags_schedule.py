# Generated migration - will be updated manually

from django.db import migrations, models
import django.db.models.deletion


def create_default_category_and_assign_products(apps, schema_editor):
    """Create a default category and assign all existing products to it"""
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')
    
    # Create default category if it doesn't exist
    default_category, created = Category.objects.get_or_create(
        slug='general',
        defaults={
            'name': 'General',
            'description': 'General products',
            'tier': 'MID_TIER',
            'is_active': True,
        }
    )
    
    # Assign all products without category to default category
    Product.objects.filter(category__isnull=True).update(category=default_category)


def reverse_migration(apps, schema_editor):
    """Reverse migration - set category to null for products in default category"""
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')
    
    try:
        default_category = Category.objects.get(slug='general')
        Product.objects.filter(category=default_category).update(category=None)
    except Category.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_product_offline_vendor_address_and_more'),
    ]

    operations = [
        # Add new fields to Category
        migrations.AddField(
            model_name='category',
            name='display_header',
            field=models.CharField(blank=True, help_text='Custom header for homepage (e.g., "Premium Picks")', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='display_tagline',
            field=models.CharField(blank=True, help_text='Tagline for homepage (e.g., "Exquisite Creations, Made Locally")', max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='category',
            name='tier',
            field=models.CharField(choices=[('PREMIUM', 'Premium/Luxury'), ('MID_TIER', 'Mid-tier'), ('AFFORDABLE', 'Affordable/Everyday')], default='MID_TIER', help_text='Category tier for segmentation', max_length=20),
        ),
        
        # Create ProductTag model
        migrations.CreateModel(
            name='ProductTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('color', models.CharField(default='#be8400', help_text='Color for tag display', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        
        # Create CategoryDisplaySchedule model
        migrations.CreateModel(
            name='CategoryDisplaySchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(choices=[('DAILY', 'Daily'), ('WEEKLY', 'Weekly'), ('MONTHLY', 'Monthly')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, help_text='Leave blank for ongoing display', null=True)),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Order on homepage (lower = first)')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='display_schedules', to='products.category')),
            ],
            options={
                'ordering': ['display_order', 'category__name'],
                'unique_together': {('category', 'period', 'start_date')},
            },
        ),
        
        # Add tags to Product (many-to-many)
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, help_text='Optional: Add tags to help customers find this product', related_name='products', to='products.producttag'),
        ),
        
        # Change category to required (PROTECT)
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(help_text='Required: Select the primary category for this product', on_delete=django.db.models.deletion.PROTECT, related_name='products', to='products.category'),
        ),
        
        # Run data migration to assign existing products to default category
        migrations.RunPython(create_default_category_and_assign_products, reverse_migration),
    ]
