# Generated by Django 5.1.2 on 2024-11-11 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0010_rename_total_price_invoiceitem_subtotal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invoiceitem',
            old_name='subtotal',
            new_name='total_price',
        ),
    ]
