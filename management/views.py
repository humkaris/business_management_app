from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from .forms import QuotationForm, QuotationItemFormSet, InvoiceForm, InvoiceItemFormSet
from .models import Quotation, QuotationItem, Invoice, InvoiceItem

def create_quotation(request, quotation_id=None):
    if quotation_id:
        # Editing an existing quotation
        quotation = get_object_or_404(Quotation, id=quotation_id)
        quotation_form = QuotationForm(request.POST or None, instance=quotation)
        formset = QuotationItemFormSet(request.POST or None, queryset=QuotationItem.objects.filter(quotation=quotation))
    else:
        # Creating a new quotation
        quotation_form = QuotationForm(request.POST or None)
        formset = QuotationItemFormSet(request.POST or None, queryset=QuotationItem.objects.none())

    if request.method == 'POST':
        if quotation_form.is_valid() and formset.is_valid():
            # Save the quotation instance
            quotation = quotation_form.save()

            # Handle formset for QuotationItem instances
            for form in formset:
                if form.cleaned_data.get('DELETE'):
                    if form.instance.pk:  # Ensure item exists before deletion
                        form.instance.delete()
                else:
                    item = form.save(commit=False)
                    item.quotation = quotation
                    item.save()

            messages.success(request, 'Quotation saved successfully!')
            return redirect('quotation_list')

    return render(request, 'management/quotation_form.html', {
        'form': quotation_form,
        'formset': formset,
    })

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

# Invoice views begin here
class InvoiceCreateView(CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    success_url = reverse_lazy('invoice_list')

    def get_initial(self):
        initial = super().get_initial()
        quotation_id = self.kwargs.get('quotation_id')
        if quotation_id:
            quotation = get_object_or_404(Quotation, id=quotation_id)
            initial.update({
                'client_name': quotation.client_name,
                'client_email': quotation.client_email,
                'client_address': quotation.client_address,
                'client_phone_number': quotation.client_phone_number,
                # Additional fields as needed
            })
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = InvoiceItemFormSet(self.request.POST)
        else:
            context['formset'] = InvoiceItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class InvoiceUpdateView(UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    success_url = reverse_lazy('invoice_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = InvoiceItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = InvoiceItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'invoices/invoice_detail.html'


class InvoiceDeleteView(DeleteView):
    model = Invoice
    template_name = 'invoices/invoice_confirm_delete.html'
    success_url = reverse_lazy('invoice_list')


class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        queryset = super().get_queryset()
        client_name = self.request.GET.get('client_name')
        status = self.request.GET.get('status')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if client_name:
            queryset = queryset.filter(client_name__icontains=client_name)
        if status:
            queryset = queryset.filter(status=status)
        if start_date and end_date:
            queryset = queryset.filter(date_created__range=[start_date, end_date])

        return queryset