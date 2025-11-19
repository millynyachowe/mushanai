# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('suppliers', '0001_initial'),
    ]

    operations = [
        # Add new fields to RawMaterial with defaults
        migrations.AddField(
            model_name='rawmaterial',
            name='approval_status',
            field=models.CharField(choices=[('PENDING', 'Pending Approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='APPROVED', max_length=20),
        ),
        migrations.AddField(
            model_name='rawmaterial',
            name='approved_by',
            field=models.ForeignKey(blank=True, limit_choices_to={'user_type': 'ADMIN'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_materials', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='rawmaterial',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rawmaterial',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rawmaterial',
            name='min_order_quantity',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
        ),
        migrations.AddField(
            model_name='rawmaterial',
            name='stock_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='rawmaterial',
            name='purchase_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='rawmaterial',
            name='total_revenue',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        
        # Modify existing fields
        migrations.AlterField(
            model_name='rawmaterial',
            name='unit',
            field=models.CharField(default='kg', max_length=50),
        ),
        migrations.AlterField(
            model_name='rawmaterial',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='rawmaterial',
            index=models.Index(fields=['approval_status', 'is_available'], name='suppliers_r_approva_idx'),
        ),
        
        # Create new models
        migrations.CreateModel(
            name='RawMaterialInquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('vendor_email', models.EmailField(max_length=254)),
                ('vendor_phone', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('NEW', 'New'), ('READ', 'Read'), ('REPLIED', 'Replied'), ('CLOSED', 'Closed')], default='NEW', max_length=20)),
                ('supplier_response', models.TextField(blank=True, null=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inquiries', to='suppliers.rawmaterial')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inquiries', to='suppliers.supplierprofile')),
                ('vendor', models.ForeignKey(limit_choices_to={'user_type': 'VENDOR'}, on_delete=django.db.models.deletion.CASCADE, related_name='material_inquiries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Raw Material Inquiries',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RawMaterialPurchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_number', models.CharField(db_index=True, max_length=100, unique=True)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit', models.CharField(max_length=50)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('PROCESSING', 'Processing'), ('SHIPPED', 'Shipped'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20)),
                ('payment_status', models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('FAILED', 'Failed')], default='PENDING', max_length=20)),
                ('delivery_address', models.TextField()),
                ('delivery_city', models.CharField(max_length=100)),
                ('delivery_phone', models.CharField(max_length=50)),
                ('vendor_notes', models.TextField(blank=True, null=True)),
                ('supplier_notes', models.TextField(blank=True, null=True)),
                ('admin_notes', models.TextField(blank=True, null=True)),
                ('ordered_at', models.DateTimeField(auto_now_add=True)),
                ('confirmed_at', models.DateTimeField(blank=True, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchases', to='suppliers.rawmaterial')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sales', to='suppliers.supplierprofile')),
                ('vendor', models.ForeignKey(limit_choices_to={'user_type': 'VENDOR'}, on_delete=django.db.models.deletion.CASCADE, related_name='raw_material_purchases', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-ordered_at'],
            },
        ),
        migrations.AddIndex(
            model_name='rawmaterialpurchase',
            index=models.Index(fields=['vendor', 'status'], name='suppliers_r_vendor__idx'),
        ),
        migrations.AddIndex(
            model_name='rawmaterialpurchase',
            index=models.Index(fields=['supplier', 'status'], name='suppliers_r_supplie_idx'),
        ),
        migrations.AddIndex(
            model_name='rawmaterialpurchase',
            index=models.Index(fields=['payment_status', 'status'], name='suppliers_r_payment_idx'),
        ),
    ]
