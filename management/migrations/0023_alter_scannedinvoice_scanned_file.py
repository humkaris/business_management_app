# Generated by Django 5.1.2 on 2025-01-03 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0022_remove_invoice_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scannedinvoice',
            name='scanned_file',
            field=models.FileField(upload_to='scanned_invoices/'),
        ),
    ]
