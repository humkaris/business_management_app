from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class Quotation(models.Model):
    client_name = models.CharField(max_length=100, blank=False, null=False)
    client_email = models.EmailField(blank=False, null=False)
    client_address = models.TextField(blank=False, null=False)
    client_phone_number = models.CharField(max_length=15, blank=False, null=False)
    
    # Custom quote fields
    quote_number = models.CharField(max_length=20, unique=True, null=True, blank=True)  # New format quote number (e.g., "QUOTE-2024-001")
    original_quote_number = models.CharField(max_length=20, blank=True, null=True)  # Original number for historical quotes
    
    date_created = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, choices=[
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Draft')
    valid_until = models.DateField(null=True, blank=True)

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
        if not self.quote_number:
            self.quote_number = self.generate_unique_quote_number()
        
        # If this is a historical quote with an existing quote number, store it in `original_quote_number`
        if self.original_quote_number is None:
            self.original_quote_number = self.quote_number
        
        self.clean()
        
        
        super().save(*args, **kwargs)

    def generate_unique_quote_number(self):
        # Find the last quote for the current year to maintain sequence
        current_year = timezone.now().year
        last_quote = Quotation.objects.filter(quote_number__startswith=f"QUOTE-{current_year}").order_by('id').last()

        if not last_quote:
            return f"QUOTE-{current_year}-001"
        
        # Extract the last sequence number and increment it
        last_sequence_number = int(last_quote.quote_number.split('-')[-1])
        new_sequence_number = last_sequence_number + 1
        return f"QUOTE-{current_year}-{new_sequence_number:03d}"

    def __str__(self):
        return f"Quotation {self.quote_number} for {self.client_name}"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")  # Link to the related quotation
    description = models.CharField(max_length=255)   # Description of the item
    quantity = models.IntegerField()                 # Quantity of the item
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit

    def total_price(self):
        return self.quantity * self.unit_price  # Calculate total for this item

    def __str__(self):
        return f"{self.description} (x{self.quantity})"

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
