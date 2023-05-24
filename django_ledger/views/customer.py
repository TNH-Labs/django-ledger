"""
Django Ledger created by Miguel Sanda <msanda@arrobalytics.com>.
Copyright© EDMA Group Inc licensed under the GPLv3 Agreement.

Contributions to this module:
Miguel Sanda <msanda@arrobalytics.com>
"""
import csv
import json

import pandas as pd
from django import forms
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
        return redirect('django_ledger:customer-list', entity_slug=entity_models[0].slug)

    def post(self, request):
        entity_slug = EntityModel.objects.for_user(user_model=request.user).first().slug
        entity_model = get_object_or_404(EntityModel, slug=entity_slug)

        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        expected_headers = ['Customer Name', 'Address', 'Phone Number', 'Country', 'Zip Code', 'Email']
        field_mapping = {
            'Customer Name': 'customer_name',
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

                customer = CustomerModel(
                    entity_model=entity_model,
                    customer_name=row['Customer Name'],
                    country=row['Country'],
                    address_1=row['Address'],
                    phone=row['Phone Number'],
                    zip_code=row['Zip Code'],
                    email=row['Email']
                )
                customer.save()
            else:
                # Add any missing headers to the list of invalid headers
                missing_headers = set(expected_headers) - set(row.keys())
                invalid_headers.append(f"Missing headers: {', '.join(missing_headers)}")

        # If there were any invalid headers, return a response indicating which headers were invalid
        if invalid_headers:
            invalid_headers_str = '<br>'.join(invalid_headers)
            messages.warning(request, f"Invalid headers:\n{invalid_headers_str}")
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



def upload_(request):
    print(f"acccessing upload of customer")

    if request.method == 'POST':
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'This is not a csv file.')
        else:

            df = pd.read_csv(csv_file)
            request.session['df'] = df.to_json(orient='split')  # Store the dataframe in the session
            fields = df.columns.tolist()
            options = [field.name for field in CustomerModel._meta.get_fields()]
            context = {'fields': fields, 'options': options}
            return render(request, 'django_ledger/customer/mapping_partial.html', context)
    else:
        # entity_models = EntityModel.objects.for_user(user_model=request.user)
        # return redirect('django_ledger:customer-list', entity_slug=entity_models[0].slug)
        return HttpResponseRedirect(reverse('django_ledger:mappingC'))



class Mapping_(DjangoLedgerSecurityMixIn, View):
    print(f"acccessing mapping of customer")
    def get(self, request, *args, **kwargs):
        entity_models = EntityModel.objects.for_user(user_model=request.user)
        entity_slug = EntityModel.objects.for_user(user_model=request.user).first().slug
        fields = request.GET.getlist('fields')
        view = reverse('django_ledger:customer-list', kwargs={'entity_slug': entity_slug})
        if 'df' in request.session:
            df = pd.read_json(request.session['df'], orient='split')

            # Filter out "Unnamed" columns
            df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

            # Add an option for "Do not save" to the choices
            choices = [(f.name, f.name) for f in CustomerModel._meta.get_fields() if not f.name.startswith('Unnamed')] + [
                ('ignore', 'Do not save')]
            field_dict = {col: forms.ChoiceField(choices=choices, widget=forms.Select(attrs={'class': 'form-control'}))
                          for col in df.columns}
            DynamicForm = type('DynamicForm', (forms.Form,), field_dict)
            print("DynamicForm:", DynamicForm, "\n\n\n")

            # context = {
            #     'fields': fields,
            #     'form': DynamicForm(),
            #     'entity_slug': entity_slug,
            #     'view': view
            # }
            # return render(request, 'django_ledger/customer/customer_list.html', context)

        return redirect('django_ledger:customer-list', entity_slug=entity_models[0].slug)


    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.session['df'])

            # Ensure the columns and data arrays have the same length
            columns = [col for col in data['columns'] if not col.startswith('Unnamed')]
            data = data['data']
            data = [row[:len(columns)] for row in data]

            df = pd.DataFrame(data, columns=columns)
        except ValueError as e:
            print("Error loading JSON into DataFrame:", e)
            print("Data:", request.session['df'])
            raise e

        mapping = {k: v for k, v in request.POST.items() if v != 'ignore'}  # Ignore columns mapped to "Do not save"
        df.rename(columns=mapping, inplace=True)

        # Remove unwanted columns
        unwanted_columns = ['ignore', 'Unnamed: 6', 'Unnamed: 7','Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 6', 'Unnamed: 7']
        df = df.drop(columns=[col for col in unwanted_columns if col in df.columns], errors='ignore')

        # Translate certain fields
        if 'status' in df.columns:  # Replace only if the 'status' column exists
            df['sent_follow_up'] = df['sent_follow_up'].apply(
                lambda x: True if x.lower() == 'yes' else False if x.lower() == 'no' else x)

        # Filter the dictionary keys based on the fields of your `customerModel`
        valid_fields = [field.name for field in CustomerModel._meta.get_fields() if not field.name.startswith('Unnamed')]
        entity_slug = EntityModel.objects.for_user(user_model=request.user).first().slug
        entity_model = get_object_or_404(EntityModel, slug=entity_slug)

        for _, row in df.iterrows():
            row_dict = row.to_dict()
            filtered_dict = {key: value for key, value in row_dict.items() if key in valid_fields}

            # Add the user to the filtered_dict
            entity_slug = EntityModel.objects.for_user(user_model=request.user).first().slug
            print(f"\n\n{entity_slug}\n\n")
            filtered_dict['entity_model'] = entity_model

            CustomerModel.objects.create(**filtered_dict)

        messages.success(request, 'Your file has been uploaded.')
        return HttpResponseRedirect(request.path)

