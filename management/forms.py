from django import forms
from django.core.exceptions import ValidationError
from .models import Quotation, QuotationItem,Invoice, InvoiceItem
from decimal import Decimal
from django.utils import timezone
from django.forms import modelformset_factory

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            'client_name', 'client_email', 'client_address', 'client_phone_number',
            'tax_rate', 'status', 'valid_until'
        ]
        labels = {
            'client_name': 'Client Name',
            'client_email': 'Client Email',
            'client_address': 'Client Address',
            'client_phone_number': 'Client Phone Number',
            'tax_rate': 'Tax Rate (%)',
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
        date_created = self.instance.date_created or timezone.now()
        valid_until = cleaned_data.get("valid_until")

        subtotal = self.instance.subtotal  # Automatically calculated in the model
        expected_labour_cost = Decimal(subtotal) * Decimal('0.30')
        grand_total = self.instance.grand_total  # Calculated in the model

        # Tax rate validation
        if tax_rate is not None and (tax_rate < Decimal('0.00') or tax_rate > Decimal('20.00')):
            raise ValidationError({'tax_rate': "Tax rate must be between 0% and 20%."})
                
        # Date validation
        if valid_until and valid_until <= date_created.date():
            raise ValidationError({"valid_until": "The valid until date must be after the date created."})
        
        # Labour cost validation
        if self.instance.labour_cost != expected_labour_cost:
            raise ValidationError({
                'labour_cost': 'Labor cost must be exactly 30% of the subtotal.'
            })

        # Ensure grand_total is greater than subtotal
        if grand_total <= subtotal:
            raise ValidationError({
                'grand_total': 'Grand total must be greater than the subtotal.'
            })

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


# Formset for handling multiple QuotationItem forms
QuotationItemFormSet = modelformset_factory(
    QuotationItem,
    form=QuotationItemForm,
    extra=1,  # Display one empty form by default
    can_delete=True  # Allow item deletion
)

# forms for Invoices begin here
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client_name', 'client_email', 'client_address', 'client_phone_number',
                  'status', 'due_date', 'tax_rate', 'stamped_invoice']
        widgets = {
            'client_address': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        quotation = kwargs.pop('quotation', None)
        super().__init__(*args, **kwargs)

        if quotation:
            # Pre-fill data from the quotation
            self.fields['client_name'].initial = quotation.client_name
            self.fields['client_email'].initial = quotation.client_email
            self.fields['client_address'].initial = quotation.client_address
            self.fields['client_phone_number'].initial = quotation.client_phone_number

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get("due_date")
        tax_rate = cleaned_data.get("tax_rate")

        # Validate due date
        if due_date and due_date <= self.instance.date_created.date():
            raise ValidationError({"due_date": "The due date must be after the invoice creation date."})

        # Tax rate validation
        if tax_rate is not None and (tax_rate < Decimal('0.00') or tax_rate > Decimal('20.00')):
            raise ValidationError({'tax_rate': "Tax rate must be between 0% and 20%."})

        return cleaned_data


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError("Quantity must be a positive integer.")
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price <= Decimal('0.00'):
            raise ValidationError("Unit price must be a positive number.")
        return unit_price

# Formset for handling multiple InvoiceItem forms
InvoiceItemFormSet = modelformset_factory(
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,  # One empty form by default
    can_delete=True  # Allow deletion of items
)