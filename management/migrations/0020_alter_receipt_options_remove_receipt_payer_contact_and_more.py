# Generated by Django 5.1.2 on 2024-11-17 15:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0019_alter_receipt_payment_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='receipt',
            options={},
        ),
        migrations.RemoveField(
            model_name='receipt',
            name='payer_contact',
        ),
        migrations.RemoveField(
            model_name='receipt',
            name='payer_name',
        ),
        migrations.RemoveField(
            model_name='receipt',
            name='payment_status',
        ),
        migrations.RemoveField(
            model_name='receipt',
            name='reference_number',
        ),
    ]
