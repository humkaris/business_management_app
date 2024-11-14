from django.urls import path
from .views import (
    InvoiceCreateView, InvoiceUpdateView, InvoiceDetailView,
    InvoiceDeleteView, InvoiceListView, create_quotation, quotation_list, edit_quotation )

urlpatterns = [
    path('create/', create_quotation, name='create_quotation'),  # Route for creating a quotation
    path('', quotation_list, name='quotation_list'),
    path('edit/<int:quotation_id>/', edit_quotation, name='edit_quotation'),
    #Invoices
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/update/', InvoiceUpdateView.as_view(), name='invoice_update'),
    path('invoices/<int:pk>/delete/', InvoiceDeleteView.as_view(), name='invoice_delete'),
    
]
