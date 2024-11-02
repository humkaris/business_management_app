from django.db import models

class Quotation(models.Model):
    quote_number = models.PositiveIntegerField(null=True, blank=True)  # or use PositiveIntegerField
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField(null=True, blank=True)  # Ensure this field is defined
    date_created = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def calculate_total(self):
        total = sum(item.total_price() for item in self.items.all())
        self.total_amount = total
        self.save()
        return total

    def __str__(self):
         return f"Quotation {self.id} for {self.client_name}"

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
