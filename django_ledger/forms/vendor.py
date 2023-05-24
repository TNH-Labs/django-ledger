"""
Django Ledger created by Miguel Sanda <msanda@arrobalytics.com>.
Copyright© EDMA Group Inc licensed under the GPLv3 Agreement.

Contributions to this module:
Miguel Sanda <msanda@arrobalytics.com>
"""

from django.forms import ModelForm, TextInput, EmailInput

from django_ledger.forms.utils import validate_cszc
from django_ledger.models import EntityModel
from django_ledger.models.vendor import VendorModel
from django_ledger.settings import DJANGO_LEDGER_FORM_INPUT_CLASSES
from django import forms

from django import forms


class VendorModelForm(ModelForm):

    def clean(self):
        validate_cszc(self.cleaned_data)

    class Meta:
        model = VendorModel
        fields = [
            'vendor_name',
            'address_1',
            'address_2',
            'city',
            'state',
            'zip_code',
            'country',
            'phone',
            'email',
            'website',
            'tax_id_number'
        ]
        widgets = {
            'vendor_name': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES
            }),
            'address_1': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES
            }),
            'address_2': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES
            }),
            'city': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES
            }),
            'state': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES
            }),
            'zip_code': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES
            }),
            'country': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES
            }),
            'phone': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES
            }),
            'email': EmailInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES
            }),
            'website': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES
            }),
            'tax_id_number': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES
            }),
        }

# class UploadCSV(forms.Form):
#     csv_file = forms.FileField(required=True)
#     entity = forms.ModelChoiceField(queryset=EntityModel.objects.none(), empty_label="Select Entity")
#
#
#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user')
#         super(UploadCSV, self).__init__(*args, **kwargs)
#         self.fields['entity'].queryset = EntityModel.objects.for_user(user_model=user)
#
#     def clean(self):
#         cleaned_data = super().clean()
#         file = cleaned_data.get('csv_file')
#         if file:
#             if file.content_type != 'text/csv':
#                 raise forms.ValidationError('File is not CSV type')
#         else:
#             raise forms.ValidationError('Couldn\'t read uploaded file')
#
#         return cleaned_data

