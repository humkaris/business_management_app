from django.db import models

from django.db import models

class Quotation(models.Model):
    quote_number = models.CharField(max_length=20, unique=True)
    client_name = models.CharField(max_length=100)
    date_created = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.quote_number

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
