# Generated by Django 5.1.2 on 2024-11-14 15:12

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0011_rename_subtotal_invoiceitem_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='stamped_invoice',
            field=models.FileField(blank=True, null=True, upload_to='scanned_invoices/'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='date_created',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
