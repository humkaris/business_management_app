from django.contrib import admin
from .models import Quotation, QuotationItem, Invoice, InvoiceItem, ScannedInvoice

class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1  # Display one empty form for adding items
    fields = ('description', 'quantity', 'unit_price', 'line_total')
    readonly_fields = ('line_total',)
    can_delete = True

    # Optional: display the line total as a calculated field
    def line_total(self, obj):
        return obj.total_price()
    line_total.short_description = 'Line Total'  # Custom header for readability

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = (
        'quote_number',
        'client_name',
        'client_email',
        'client_address',
        'client_phone_number',
        'subtotal',
        'labour_cost',
        'total_tax',
        'grand_total',
        'status',  
        'date_created'
    )
    search_fields = ('client_name', 'client_email', 'quote_number')
    list_filter = ('status',)
    ordering = ('-date_created',)
    readonly_fields = ('quote_number', 'subtotal', 'total_tax', 'labour_cost', 'grand_total')

    # Integrate QuotationItemInline to allow editing items on the same page
    inlines = [QuotationItemInline]


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1  # Number of empty forms to display initially
    fields = ('description', 'quantity', 'unit_price', 'total_price')
    readonly_fields = ('total_price',)
    can_delete = True
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'client_name', 
        'client_email',
        'client_address',
        'client_phone_number',
        'status',
        'date_created', 
        'due_date', 
        'total_tax',
        'grand_total'
    )
    search_fields = ('invoice_number', 'client_name')
    list_filter = ('status',)
    ordering = ('-date_created',)
    readonly_fields = ('invoice_number', 'total_tax', 'grand_total', 'labour_cost')  # Display tax and grand total
    inlines = [InvoiceItemInline]

    def save_model(self, request, obj, form, change):
        # Automatically pull billing details from the quotation if linked
        if obj.quotation:
            obj.client_name = obj.quotation.client_name
            obj.client_email = obj.quotation.client_email
            obj.client_address = obj.quotation.client_address
            obj.client_phone_number = obj.quotation.client_phone_number
            obj.subtotal = obj.quotation.subtotal
            obj.total_tax = obj.quotation.total_tax
            obj.grand_total = obj.quotation.grand_total
        else:
            # If no quotation is linked, calculate totals for standalone invoice
            obj.calculate_totals()

        super().save_model(request, obj, form, change)


    def get_readonly_fields(self, request, obj=None):
        """
        Set fields to read-only based on whether the invoice is linked to a quotation.
        """
        readonly_fields = super().get_readonly_fields(request, obj)
        if not obj or not obj.quotation:
            # Hide 'labour_cost' if there is no quotation
            return readonly_fields + ('labour_cost',)
        return readonly_fields
class ScannedInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'scanned_file', 'date_uploaded']
    search_fields = ['invoice__invoice_number']  # Optional: Allows searching by invoice number

admin.site.register(ScannedInvoice, ScannedInvoiceAdmin)