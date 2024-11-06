from django import forms
from django.core.exceptions import ValidationError
from .models import Quotation, QuotationItem
from decimal import Decimal
from django.utils import timezone

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            'client_name', 'client_email', 'client_address', 'client_phone_number',
            'tax_rate', 'labour_cost', 'status', 'valid_until'
        ]
        labels = {
            'client_name': 'Client Name',
            'client_email': 'Client Email',
            'client_address': 'Client Address',
            'client_phone_number': 'Client Phone Number',
            'tax_rate': 'Tax Rate (%)',
            'labour_cost': 'Labor Cost (Auto-calculated as 30% of subtotal)',
            'status': 'Status',
            'valid_until': 'Valid Until',
        }
        widgets = {
            'client_address': forms.Textarea(attrs={'rows': 3}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tax_rate = cleaned_data.get("tax_rate")
        date_created = cleaned_data.get("date_created") or timezone.now()
        valid_until = cleaned_data.get("valid_until")

        # Tax rate validation
        if tax_rate is not None:
            if tax_rate < Decimal('0.00') or tax_rate > Decimal('20.00'):
                raise ValidationError({'tax_rate': "Tax rate must be between 0% and 20%."})
                

        # Date validation
        if valid_until and date_created:
            if valid_until <= date_created.date():
                raise ValidationError({"valid_until": "The valid until date must be after the date created."})
       
        return cleaned_data



class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ['description', 'quantity', 'unit_price']
        labels = {
            'description': 'Item Description',
            'quantity': 'Quantity',
            'unit_price': 'Unit Price',
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise ValidationError("Quantity must be a positive integer.")
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price is not None and unit_price <= Decimal('0.00'):
            raise ValidationError("Unit price must be a positive number.")
        return unit_price