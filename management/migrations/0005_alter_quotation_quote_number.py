# Generated by Django 5.1.2 on 2024-11-04 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0004_alter_quotation_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotation',
            name='quote_number',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]