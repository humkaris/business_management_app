from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import QuotationForm, QuotationItemForm
from .models import Quotation, QuotationItem


def create_quotation(request):
    if request.method == 'POST':
        form = QuotationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quotation created successfully!')
            return redirect('quotation_list')  # Redirect to a list of quotations or another page
    else:
        form = QuotationForm()

    return render(request, 'management/create_quotation.html', {'form': form})

def quotation_list(request):
    quotations = Quotation.objects.all()  # Fetch all quotations from the database
    return render(request, 'management/quotation_list.html', {'quotations': quotations})


def edit_quotation(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)  # Fetch the quotation by ID
    if request.method == 'POST':
        form = QuotationForm(request.POST, instance=quotation)  # Bind the form to the existing quotation
        if form.is_valid():
            form.save()
            messages.success(request, 'Quotation updated successfully!')
            return redirect('quotation_list')  # Redirect to the quotation list
    else:
        form = QuotationForm(instance=quotation)  # Pre-fill the form with the existing quotation data

    return render(request, 'management/quotation_form.html', {'form': form})