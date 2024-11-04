from django.contrib import admin
from .models import Quotation, QuotationItem

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = (
        'client_name',
        'client_email',
        'client_address',
        'client_phone_number',
        'quote_number',
        'subtotal',
        'total_tax',
        'grand_total',
        'status',  # Display the status of the quotation
        'date_created'  # You might also want to display the creation date
    )
    search_fields = ('client_name', 'client_email', 'quote_number')
    list_filter = ('status',)  # Allows filtering by status in the admin
    ordering = ('-date_created',)  # Orders the quotations by creation date, newest first
    readonly_fields = ('quote_number', 'subtotal', 'total_tax', 'grand_total')  # Make financial fields read-only

@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = (
        'quotation',
        'description',
        'quantity',
        'unit_price',
        'line_total',  # You can use total_price method from QuotationItem
    )
    search_fields = ('description',)  # Allows searching by item description
    list_filter = ('quotation',)  # Allows filtering by related quotation
    ordering = ('quotation',)

    # You may want to display the line_total in a more readable way
    def line_total(self, obj):
        return obj.total_price()  # Call the total_price method
    line_total.short_description = 'Line Total'  # This sets the column header in the admin
