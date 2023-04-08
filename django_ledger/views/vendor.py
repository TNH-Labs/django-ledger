"""
Django Ledger created by Miguel Sanda <msanda@arrobalytics.com>.
Copyright© EDMA Group Inc licensed under the GPLv3 Agreement.

Contributions to this module:
Miguel Sanda <msanda@arrobalytics.com>
"""
import io

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib import messages

from django_ledger.forms.vendor import VendorModelForm
from django_ledger.models.entity import EntityModel
from django_ledger.models.vendor import VendorModel
from django_ledger.views.mixins import DjangoLedgerSecurityMixIn
from django.views import View

import csv

from django.views import View
from django.http import HttpResponse
from django.shortcuts import render
import csv

class ImportCSV(View):
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
            # return HttpResponse(f"No EntityModel found for entity_name: {entity_name}")

        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        expected_headers = ['Vendor Name', 'Address', 'Phone Number', 'Country', 'Zip Code', 'Email']
        field_mapping = {
            'Vendor Name': 'vendor_name',
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

                vendor = VendorModel(
                    entity_model=entity_model,
                    vendor_name=row['Vendor Name'],
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
            # return HttpResponse(f"Invalid headers:<br>{invalid_headers_str}")
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


class VendorModelModelViewQuerySetMixIn:
    queryset = None

    def get_queryset(self):
        if not self.queryset:
            self.queryset = VendorModel.objects.for_entity(
                entity_slug=self.kwargs['entity_slug'],
                user_model=self.request.user
            ).order_by('-updated')
        return super().get_queryset()


class VendorModelListView(DjangoLedgerSecurityMixIn, VendorModelModelViewQuerySetMixIn, ListView):
    template_name = 'django_ledger/vendor/vendor_list.html'
    context_object_name = 'vendors'
    PAGE_TITLE = _('Vendor List')
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
        'header_subtitle_icon': 'bi:person-lines-fill'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entities = EntityModel.objects.all()
        print("\n\n\nentites ", entities)
        context['entities'] = entities
        context['extra_content'] = {
            'entity_list': entities
        }
        return context


class VendorModelCreateView(DjangoLedgerSecurityMixIn, VendorModelModelViewQuerySetMixIn, CreateView):
    template_name = 'django_ledger/vendor/vendor_create.html'
    PAGE_TITLE = _('Create New Vendor')
    form_class = VendorModelForm
    context_object_name = 'vendor'
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
        'header_subtitle_icon': 'bi:person-lines-fill'
    }

    def get_success_url(self):
        return reverse('django_ledger:vendor-list',
                       kwargs={
                           'entity_slug': self.kwargs['entity_slug']
                       })

    def form_valid(self, form):
        vendor_model: VendorModel = form.save(commit=False)
        entity_model_qs = EntityModel.objects.for_user(
            user_model=self.request.user
        )
        entity_model = get_object_or_404(klass=entity_model_qs, slug__exact=self.kwargs['entity_slug'])
        vendor_model.entity_model = entity_model
        return super().form_valid(form)


class VendorModelUpdateView(DjangoLedgerSecurityMixIn, VendorModelModelViewQuerySetMixIn, UpdateView):
    template_name = 'django_ledger/vendor/vendor_update.html'
    PAGE_TITLE = _('Vendor Update')
    context_object_name = 'vendor'
    form_class = VendorModelForm

    slug_url_kwarg = 'vendor_pk'
    slug_field = 'uuid'

    def get_context_data(self, **kwargs):
        context = super(VendorModelUpdateView, self).get_context_data(**kwargs)
        vendor_model: VendorModel = self.object
        context['page_title'] = self.PAGE_TITLE
        context['header_title'] = self.PAGE_TITLE
        context['header_subtitle'] = vendor_model.vendor_number
        context['header_subtitle_icon'] = 'bi:person-lines-fill'
        return context

    def get_success_url(self):
        return reverse('django_ledger:vendor-list',
                       kwargs={
                           'entity_slug': self.kwargs['entity_slug']
                       })

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class VendorModelDeleteView(DjangoLedgerSecurityMixIn, VendorModelModelViewQuerySetMixIn, View):
    def get(self, request, *args, **kwargs):
        vendor_model = get_object_or_404(self.get_queryset(), uuid=kwargs['vendor_pk'])
        vendor_model.delete()
        messages.success(request, 'Vendor was successfully deleted.')
        return redirect('django_ledger:vendor-list', entity_slug=kwargs['entity_slug'])

    def get_queryset(self):
        return VendorModel.objects.for_entity(
            entity_slug=self.kwargs['entity_slug'],
            user_model=self.request.user
        ).order_by('-updated')


