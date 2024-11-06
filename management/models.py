from django.db import models
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class Quotation(models.Model):
    client_name = models.CharField(max_length=100, blank=False, null=False)
    client_email = models.EmailField(blank=False, null=False)
    client_address = models.TextField(blank=False, null=False)
    client_phone_number = models.CharField(max_length=15, blank=False, null=False)
    
    # Custom quote fields
    quote_number = models.CharField(max_length=200, unique=True, null=True, blank=True)  # New format quote number (e.g., "QUOTE-2024-001")
    original_quote_number = models.CharField(max_length=200, blank=True, null=True)  # Original number for historical quotes
    
    date_created = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, choices=[
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Draft')
    valid_until = models.DateField(null=True, blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    labour_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add labor cost
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Tax rate as a percentage
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Calculated tax amount
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total amount including labor and tax


    def calculate_totals(self):
        """Calculate subtotal, tax, and grand total."""
        # Calculate subtotal as the sum of all item totals
        self.subtotal = sum(item.total_price() for item in self.items.all())
        
        # Calculate total tax based on tax rate
        self.total_tax = (self.subtotal * self.tax_rate / 100)  # Assuming tax_rate is a percentage
        

         # Set labor cost to 30% of the subtotal
        self.labour_cost = self.subtotal * Decimal('0.30')
        # Calculate grand total
        self.grand_total = self.subtotal + Decimal(self.total_tax) + self.labour_cost

        

    def clean(self):
        # Validate email format
        try:
            validate_email(self.client_email)
        except ValidationError:
            raise ValidationError("Invalid email format")

        # Check for required fields (Django will also check blank/null constraints)
        if not self.client_name:
            raise ValidationError("Client name is required.")
        if not self.client_address:
            raise ValidationError("Client address is required.")
        if not self.client_phone_number:
            raise ValidationError("Client phone number is required.")

    def save(self, *args, **kwargs):
        # Check if this is a new entry without an assigned `quote_number`
        if not self.pk:  # Only generate if this is a new instance
            self.quote_number = self.generate_unique_quote_number()
        
        self.clean()

        if self.pk is None:  # This is a new instance
            super().save(*args, **kwargs)  # Save without update_fields

        self.calculate_totals()

        super().save(*args, **kwargs)

    def generate_unique_quote_number(self):
        current_year = timezone.now().year
        last_quote = (
            Quotation.objects
            .filter(quote_number__startswith=f"QUOTE-{current_year}-")
            .order_by('quote_number')
            .last()
        )

        if not last_quote:
            print("Generating first quote number for the year")
            return f"QUOTE-{current_year}-001"

        last_sequence_number = int(last_quote.quote_number.split('-')[-1])
        new_sequence_number = last_sequence_number + 1

        # Generate the new quote number
        new_quote_number = f"QUOTE-{current_year}-{new_sequence_number:03d}"

        # Check if the new quote number already exists (which should not happen)
        while Quotation.objects.filter(quote_number=new_quote_number).exists():
            print(f"Duplicate found: {new_quote_number}, trying next.")
            new_sequence_number += 1
            new_quote_number = f"QUOTE-{current_year}-{new_sequence_number:03d}"

        print(f"Generated quote number: {new_quote_number}")
        return new_quote_number


    def __str__(self):
        return f"Quotation {self.quote_number} for {self.client_name}"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")  # Link to the related quotation
    description = models.CharField(max_length=255)   # Description of the item
    quantity = models.IntegerField()                 # Quantity of the item
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit

    def total_price(self):
        return self.quantity * self.unit_price  # Calculate total for this item

    def save(self, *args, **kwargs):
        # Save the QuotationItem and trigger recalculation on the parent Quotation
        super().save(*args, **kwargs)
        self.quotation.calculate_totals()
        self.quotation.save()

    def delete(self, *args, **kwargs):
        # Delete the item and trigger recalculation on the parent Quotation
        super().delete(*args, **kwargs)
        self.quotation.calculate_totals()
        self.quotation.save()

    def __str__(self):
        return f"{self.description} (x{self.quantity})"

# additional models
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True)
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.invoice_number

class Receipt(models.Model):
    receipt_number = models.CharField(max_length=20, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.receipt_number
