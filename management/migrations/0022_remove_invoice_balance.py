# Generated by Django 5.1.2 on 2025-01-03 06:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0021_invoice_balance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='balance',
        ),
    ]