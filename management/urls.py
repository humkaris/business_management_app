from django.urls import path
from .views import create_quotation, quotation_list, edit_quotation# Import the view

urlpatterns = [
    path('create/', create_quotation, name='create_quotation'),  # Route for creating a quotation
    path('', quotation_list, name='quotation_list'),
     path('edit/<int:quotation_id>/', edit_quotation, name='edit_quotation'),
]
