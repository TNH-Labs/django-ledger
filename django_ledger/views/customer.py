"""
Django Ledger created by Miguel Sanda <msanda@arrobalytics.com>.
Copyright© EDMA Group Inc licensed under the GPLv3 Agreement.

Contributions to this module:
Miguel Sanda <msanda@arrobalytics.com>
"""
import csv

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, CreateView, UpdateView

from django_ledger.forms.customer import CustomerModelForm
from django_ledger.models.customer import CustomerModel
from django_ledger.models.entity import EntityModel
from django_ledger.views.mixins import DjangoLedgerSecurityMixIn

class ImportCSV_Customer(View):
    def get(self, request):
        entity_models = EntityModel.objects.for_user(user_model=request.user)
        context = {
            'entities': entity_models,
        }
        print("\n\n\nEntity Models: ", entity_models, "\n\n\n")
        return redirect('django_ledger:customer-list', entity_slug=entity_models[0].slug)

    def post(self, request):
        entity_name = request.POST.get('entity')

        entity_model_qs = EntityModel.objects.for_user(user_model=self.request.user)
        entity_model = entity_model_qs.filter(name__exact=entity_name).first()

        if not entity_model:
            messages.warning(request, f"No EntityModel found for entity_name: {entity_name}")
            return HttpResponseRedirect(request.path)
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        expected_headers = ['Customer Name', 'Address', 'Phone Number', 'Country', 'Zip Code', 'Email']
        field_mapping = {
            'Customer Name': 'vendor_name',
            'Address': 'address',
            'Phone Number': 'phone_number',
            'Country': 'country',
            'Zip Code': 'zip_code',
            'Email': 'email'
        }

        invalid_headers = []

        for row in reader:
            if all(header in row for header in expected_headers):
                mapped_data = {field_mapping[header]: row[header] for header in expected_headers}

                vendor = CustomerModel(
                    entity_model=entity_model,
                    customer_name=row['Customer Name'],
                    country=row['Country'],
                    address_1=row['Address'],
                    phone=row['Phone Number'],
                    zip_code=row['Zip Code'],
                    email=row['Email']
                )
                vendor.save()
            else:
                # Add any missing headers to the list of invalid headers
                missing_headers = set(expected_headers) - set(row.keys())
                invalid_headers.append(f"Missing headers: {', '.join(missing_headers)}")

        # If there were any invalid headers, return a response indicating which headers were invalid
        if invalid_headers:
            invalid_headers_str = '<br>'.join(invalid_headers)
            messages.warning(request, f"Invalid headers:<br>{invalid_headers_str}")
            return HttpResponseRedirect(request.path)
        else:
            # Return a response indicating that the data was successfully imported
            messages.success(request, f"Successfully imported")
            return HttpResponseRedirect(request.path)

    def dispatch(self, request, *args, **kwargs):
        # Override the dispatch method to enforce CSRF protection on POST requests
        if request.method == 'POST':
            return csrf_protect(self.post)(request, *args, **kwargs)
        else:
            return super().dispatch(request, *args, **kwargs)


class CustomerModelModelViewQuerySetMixIn:
    queryset = None

    def get_queryset(self):
        if not self.queryset:
            self.queryset = CustomerModel.objects.for_entity(
                entity_slug=self.kwargs['entity_slug'],
                user_model=self.request.user
            ).order_by('-updated')
        return super().get_queryset()


class CustomerModelListView(DjangoLedgerSecurityMixIn,
                            CustomerModelModelViewQuerySetMixIn,
                            ListView):
    template_name = 'django_ledger/customer/customer_list.html'
    PAGE_TITLE = _('Customer List')
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
        'header_subtitle_icon': 'dashicons:businesswoman'
    }
    context_object_name = 'customers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entities = EntityModel.objects.all()
        print("\n\n\nentites ", entities)
        context['entities'] = entities
        context['extra_content'] = {
            'entity_list': entities
        }
        return context


class CustomerModelCreateView(DjangoLedgerSecurityMixIn,
                              CustomerModelModelViewQuerySetMixIn,
                              CreateView):
    template_name = 'django_ledger/customer/customer_create.html'
    PAGE_TITLE = _('Create New Customer')
    form_class = CustomerModelForm
    context_object_name = 'customer'
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
        'header_subtitle_icon': 'dashicons:businesswoman'
    }

    def get_success_url(self):
        return reverse('django_ledger:customer-list',
                       kwargs={
                           'entity_slug': self.kwargs['entity_slug']
                       })

    def form_valid(self, form):
        customer_model: CustomerModel = form.save(commit=False)
        entity_model = EntityModel.objects.for_user(
            user_model=self.request.user
        ).get(slug__exact=self.kwargs['entity_slug'])
        customer_model.entity_model = entity_model
        customer_model.save()
        return super().form_valid(form)


class CustomerModelUpdateView(DjangoLedgerSecurityMixIn,
                              CustomerModelModelViewQuerySetMixIn,
                              UpdateView):
    template_name = 'django_ledger/customer/customer_update.html'
    PAGE_TITLE = _('Customer Update')
    form_class = CustomerModelForm
    context_object_name = 'customer'
    slug_url_kwarg = 'customer_pk'
    slug_field = 'uuid'

    def get_context_data(self, **kwargs):
        context = super(CustomerModelUpdateView, self).get_context_data(**kwargs)
        customer_model: CustomerModel = self.object
        context['page_title'] = self.PAGE_TITLE
        context['header_title'] = self.PAGE_TITLE
        context['header_subtitle'] = customer_model.customer_number
        context['header_subtitle_icon'] = 'dashicons:businesswoman'
        return context

    def get_success_url(self):
        return reverse('django_ledger:customer-list',
                       kwargs={
                           'entity_slug': self.kwargs['entity_slug']
                       })

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class CustomerModelDeleteView(DjangoLedgerSecurityMixIn, CustomerModelModelViewQuerySetMixIn, View):
    def get(self, request, *args, **kwargs):
        customer_model = get_object_or_404(self.get_queryset(), uuid=kwargs['customer_pk'])
        customer_model.delete()
        messages.success(request, 'Customer was successfully deleted.')
        return redirect('django_ledger:customer-list', entity_slug=kwargs['entity_slug'])

    def get_queryset(self):
        return CustomerModel.objects.for_entity(
            entity_slug=self.kwargs['entity_slug'],
            user_model=self.request.user
        ).order_by('-updated')
#
# from django.urls import reverse_lazy
# from django.contrib.messages.views import SuccessMessageMixin
# from django.shortcuts import get_object_or_404
# from django.views.generic import DeleteView
#
# from django_ledger.models.customer import CustomerModel
# from django_ledger.views.mixins import DjangoLedgerSecurityMixIn
#
#
# class CustomerModelDeleteView(DjangoLedgerSecurityMixIn, SuccessMessageMixin, DeleteView):
#     model = CustomerModel
#     context_object_name = 'customer'
#     slug_url_kwarg = 'customer_pk'
#     success_message = 'Customer was deleted successfully.'
#
#     def get_success_url(self):
#         return reverse_lazy('django_ledger:customer-list', kwargs={'entity_slug': self.kwargs['entity_slug']})
#
#     def get_object(self, queryset=None):
#         customer = get_object_or_404(CustomerModel, uuid=self.kwargs['customer_pk'])
#         return customer
