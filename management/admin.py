from django.contrib import admin
from .models import Quotation

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_email', 'client_address', 'client_phone_number')
    search_fields = ('client_name', 'client_email')