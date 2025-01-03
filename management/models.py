from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


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
        """Calculate subtotal, tax, and grand total without triggering infinite recursion."""
        self.subtotal = sum(item.total_price() for item in self.items.all())
        self.labour_cost = self.subtotal * Decimal('0.30')

        # Ensure tax_rate is Decimal for compatibility in calculations
        tax_rate_decimal = Decimal(self.tax_rate)

        # Calculate total tax based on the updated formula, rounded to 2 decimal places
        self.total_tax = ((self.subtotal + self.labour_cost) * (tax_rate_decimal / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Calculate the grand total
        self.grand_total = (self.subtotal + self.labour_cost + self.total_tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        

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
        if self.quantity is not None and self.unit_price is not None:
            return self.quantity * self.unit_price
        return 0
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

class Invoice(models.Model):
    # Fields for Invoice model
    invoice_number = models.CharField(max_length=20, unique=True)
    quotation = models.ForeignKey('Quotation', on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    client_name = models.CharField(max_length=100, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    client_address = models.TextField(blank=True, null=True)
    client_phone_number = models.CharField(max_length=15, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    labour_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=50,
        choices=[
            ('Draft', 'Draft'),
            ('Sent', 'Sent'),
            ('Paid', 'Paid'),
            ('Overdue', 'Overdue'),
            ('Unpaid', 'Unpaid'),
            ('Partially Paid', 'Partially Paid'),
        ],
        default='Draft'
    )
    stamped_invoice = models.FileField(upload_to='scanned_invoices/', null=True, blank=True)

    def calculate_outstanding_balance(self):
        """Calculate the outstanding balance of the invoice."""
        total_paid = sum(receipt.amount_paid for receipt in self.receipts.all())
        return Decimal(self.grand_total) - Decimal(total_paid)

    def update_payment_status(self, save_instance=False):
        """Update the payment status of the invoice."""
        outstanding_balance = self.calculate_outstanding_balance()
        new_status = (
            'Paid' if outstanding_balance <= 0 else
            'Partially Paid' if outstanding_balance < self.grand_total else
            'Unpaid'
        )
        if self.status != new_status:
            self.status = new_status
            if save_instance:
                super().save(update_fields=['status'])
    
    def get_balance(self):
        """Calculate the balance for the invoice."""
        outstanding_balance = self.calculate_outstanding_balance()
        
        if outstanding_balance == self.grand_total:
            return "UNPAID"
        elif outstanding_balance <= 0:
            return "CLEARED"
        else:
            return outstanding_balance

    def calculate_totals(self):
        """Calculate totals for invoices, including tax and grand total."""
        subtotal = Decimal(self.subtotal)
        labour_cost = Decimal(self.labour_cost)
        tax_rate = Decimal(self.tax_rate) / 100
        self.total_tax = (subtotal + labour_cost) * tax_rate
        self.grand_total = subtotal + labour_cost + self.total_tax
        

    def save(self, *args, **kwargs):
        is_new_invoice = self.pk is None

        if not self.invoice_number:
            self.invoice_number = self.generate_unique_invoice_number()
        
        if is_new_invoice:
            super().save(*args, **kwargs)

        if self.quotation:
            self._populate_from_quotation(is_new_invoice)
        else:
            self.calculate_totals()

        super().save(*args, **kwargs)
        self.update_payment_status(save_instance=True)

    def _populate_from_quotation(self, is_new_invoice):
        """Populate invoice fields from the linked quotation."""
        self.client_name = self.quotation.client_name
        self.client_email = self.quotation.client_email
        self.client_address = self.quotation.client_address
        self.client_phone_number = self.quotation.client_phone_number
        self.subtotal = self.quotation.subtotal
        self.labour_cost = self.quotation.labour_cost
        self.total_tax = self.quotation.total_tax
        self.grand_total = self.quotation.grand_total

        if is_new_invoice and not self.items.exists():
            super().save()  # Save to get an ID for the invoice
            for item in self.quotation.items.all():
                InvoiceItem.objects.create(
                    invoice=self,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price
                )

    def generate_unique_invoice_number(self):
        """Generate a unique invoice number."""
        current_year = timezone.now().year
        last_invoice = Invoice.objects.filter(invoice_number__startswith=f"INV-{current_year}-").last()
        new_sequence_number = 1 if not last_invoice else int(last_invoice.invoice_number.split('-')[-1]) + 1
        return f"INV-{current_year}-{new_sequence_number:03d}"

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.client_name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description


@receiver(post_save, sender=InvoiceItem)
def update_invoice_totals(sender, instance, **kwargs):
    """Update the invoice totals after saving an InvoiceItem."""
    invoice = instance.invoice
    invoice.calculate_totals()
    invoice.save()


class ScannedInvoice(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    scanned_file = models.FileField(upload_to= 'scanned_invoices/')
    date_uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scanned Invoice for {self.invoice.invoice_number}"


# this model class is for both invoice and quotation
class Footnote(models.Model):
    quotation_text = models.TextField(
        default="Above information is not an invoice and only an estimate of services/goods described above. "
                "Payment will be collected in prior to provision of services/goods described in this quote. "
                "Please confirm your acceptance of this quote by signing this document.\n\n"
                "Signature       Print Name       Date\n\n"
                "Thank you for your business!\n"
                "Should you have any enquiries concerning this quote, please contact:\n"
                "Ken 0731 011 954 | Humphrey 0715 679 643"
    )
    invoice_text = models.TextField(
        default="PAYMENT DETAILS:\n"
                "PAYBILL: 522522\n"
                "ACCOUNT: 5808345\n"
                "----------------------------------\n"
                "KCB BANK\n"
                "ACCOUNT: 1295384434\n\n"
                "Please confirm your Receipt of this Invoice by signing this document.\n\n"
                "Signature               Print Name                                      Date\n\n"
                "Thank you for your business!\n"
                "Should you have any enquiries concerning this Invoice, please contact:\n"
                "Ken 0707 475 681 | Humphrey 0715 679 643"
    )

    def __str__(self):
        return "Footnotes for Quotations and Invoices"

# Receipt Model begins here
class Receipt(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
        ('Mobile Money', 'Mobile Money'),
        ('Other', 'Other'),
    ]

    receipt_number = models.CharField(max_length=20, unique=True, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='receipts')
    payment_date = models.DateField(default=timezone.now)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def clean(self):
        outstanding_balance = self.invoice.calculate_outstanding_balance()
        if self.amount_paid > outstanding_balance:
            raise ValueError(f"Amount paid cannot exceed the outstanding balance of {outstanding_balance}.")
        if self.amount_paid <= Decimal('0.00'):
            raise ValueError("Amount paid must be greater than zero.")

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_unique_receipt_number()
        self.clean()
        super().save(*args, **kwargs)
        self.invoice.update_payment_status(save_instance=True)

    def generate_unique_receipt_number(self):
        current_year = timezone.now().year
        last_receipt = Receipt.objects.filter(receipt_number__startswith=f"RCT-{current_year}-").last()
        new_sequence_number = 1 if not last_receipt else int(last_receipt.receipt_number.split('-')[-1]) + 1
        return f"RCT-{current_year}-{new_sequence_number:03d}"

    def __str__(self):
        return f"Receipt {self.receipt_number} for Invoice {self.invoice.invoice_number} - {self.amount_paid} paid on {self.payment_date}"

