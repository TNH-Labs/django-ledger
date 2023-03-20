import io

from django.forms import (ModelForm, DateInput, TextInput, Select,
                          CheckboxInput, BaseModelFormSet,
                          modelformset_factory, Textarea, DateTimeInput)
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from django_ledger.io.roles import ASSET_CA_CASH, ASSET_CA_PREPAID, LIABILITY_CL_ACC_PAYABLE
from django_ledger.models import (ItemModel, AccountModel, BillModel, ItemTransactionModel,
                                  VendorModel, EntityUnitModel)
from django_ledger.settings import DJANGO_LEDGER_FORM_INPUT_CLASSES

from django import forms
# from .models import BillModel
# from .models import BillModelAbstract
# """import bill models."""
#  import BillModelAbstract
from django_ledger.models.bill import BillModel

from django import forms

#addition
class UploadCSVForm(forms.Form):
    csv_file = forms.FileField(label='Select a CSV file')
    string_to_match = forms.CharField(label='Enter header to match')


















# class BillUploadForm(forms.ModelForm):
#     csv_file = forms.FileField(label='CSV File', help_text='Please upload a CSV file.')
#
#     class Meta:
#         model = BillModel
#         fields = ()
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         csv_file = self.cleaned_data.get('csv_file')
#
#         # read CSV file
#         csv_data = csv.reader(io.StringIO(csv_file.read().decode('utf-8-sig')))
#         print("csv_data: ", csv_data)
#
#         # match headers and extract data
#         header = next(csv_data)
#         vendor_index = header.index('Vendor')
#         xref_index = header.index('xref (External Reference Number)')
#         draft_date_index = header.index('Draft Date')
#         terms_index = header.index('Terms')
#         cash_account_index = header.index('Cash Account')
#         prepaid_expenses_account_index = header.index('Prepaid Expenses Account')
#         payable_account_index = header.index('Payable Account')
#
#         for row in csv_data:
#             vendor = row[vendor_index]
#             xref = row[xref_index]
#             draft_date = row[draft_date_index]
#             terms = row[terms_index]
#             cash_account = row[cash_account_index]
#             prepaid_expenses_account = row[prepaid_expenses_account_index]
#             payable_account = row[payable_account_index]
#
#             # save data to BillModel instance
#             instance.vendor = vendor
#             instance.xref = xref
#             instance.date_draft = draft_date
#             instance.terms = terms
#             instance.cash_account = cash_account
#             instance.prepaid_expenses_account = prepaid_expenses_account
#             instance.payable_account = payable_account
#
#             if commit:
#                 instance.save()
#
#         return instance




# class BillUploadForm(forms.ModelForm):
#     class Meta:
#         model = BillModel
#         fields = ('bill_date', 'bill_number', 'vendor_name', 'vendor_address', 'total_amount', 'description', 'category')
#
#     csv_file = forms.FileField()
#
#     def clean_csv_file(self):
#         csv_file = self.cleaned_data['csv_file']
#         # Do some validation on the csv file
#         return csv_file
#
#     def save(self):
#         bill_model = super().save(commit=False)
#
#         # Do some processing on the csv file and update the bill_model fields accordingly
#         # ...
#
#         bill_model.save()
#
#         return bill_model

import csv


# class BillUploadForm(forms.ModelForm):
#     csv_file = forms.FileField(label='Upload CSV file', required=True)
#
#     class Meta:
#         model = BillModel
#         exclude = ['bill_number']
#         fields = ('Status', 'Status Date', 'Vendor', 'Amount Due', 'Payments', 'Past Due')
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#
#         csv_file = self.cleaned_data['csv_file']
#         decoded_file = csv_file.read().decode('utf-8').splitlines()
#         reader = csv.DictReader(decoded_file)
#
#         # Get the list of headers from the CSV file
#         headers = [header.lower() for header in reader.fieldnames]
#
#         # Map the headers to the fields in the BillModel
#         field_mapping = {
#             'status': 'Status',
#             'bill_date': 'Status Date',
#             'vendor': 'Vendor',
#             'total_amount': 'Amount Due',
#             'payments': 'Payments',
#             'past_due': 'Past Due',
#
#         }
#
#         # Initialize the values of the fields
#         for field_name in self.fields.keys():
#             if field_name in ['csv_file']:
#                 continue
#
#             if field_name == 'vendor':
#                 vendor_field_value = instance.vendor.pk if instance.vendor else None
#                 setattr(instance, field_name, vendor_field_value)
#             else:
#                 setattr(instance, field_name, None)
#
#         for row in reader:
#             # Map the values from the CSV file to the fields in the BillModel
#             for field_name, header in field_mapping.items():
#                 if header.lower() in headers:
#                     value = row[header.lower()].strip()
#                     if field_name == 'vendor':
#                         try:
#                             vendor = VendorModel.objects.get(pk=value)
#                             print("\n\n\nvendor: ", vendor)
#                             setattr(instance, field_name, vendor)
#                         except VendorModel.DoesNotExist:
#                             pass
#                     elif field_name == 'bill_items':
#                         # Split the string and create a list of BillItemModel instances
#                         item_ids = value.split(',')
#                         items = []
#                         for item_id in item_ids:
#                             try:
#                                 item = BillModel.objects.get(pk=item_id)
#                                 items.append(item)
#                             except BillModel.DoesNotExist:
#                                 pass
#                         setattr(instance, field_name, items)
#                     else:
#                         setattr(instance, field_name, value)
#
#             if commit:
#                 instance.save()
#
#         return instance




class BillModelCreateForm(ModelForm):
    def __init__(self, *args, entity_slug, user_model, **kwargs):
        super().__init__(*args, **kwargs)
        self.ENTITY_SLUG = entity_slug
        self.USER_MODEL = user_model
        self.BILL_MODEL: BillModel = self.instance
        self.get_vendor_queryset()
        self.get_accounts_queryset()

    def get_vendor_queryset(self):
        if 'vendor' in self.fields:
            vendor_qs = VendorModel.objects.for_entity(
                user_model=self.USER_MODEL,
                entity_slug=self.ENTITY_SLUG
            )
            self.fields['vendor'].queryset = vendor_qs

    def get_accounts_queryset(self):

        if all([
            'cash_account' in self.fields,
            'prepaid_account' in self.fields,
            'unearned_account' in self.fields,
        ]):
            account_qs = AccountModel.objects.for_bill(
                user_model=self.USER_MODEL,
                entity_slug=self.ENTITY_SLUG
            )

            # forcing evaluation of qs to cache results for fields... (avoids multiple database queries)
            len(account_qs)

            self.fields['cash_account'].queryset = account_qs.filter(role__exact=ASSET_CA_CASH)
            self.fields['prepaid_account'].queryset = account_qs.filter(role__exact=ASSET_CA_PREPAID)
            self.fields['unearned_account'].queryset = account_qs.filter(role__exact=LIABILITY_CL_ACC_PAYABLE)

    class Meta:
        model = BillModel
        fields = [
            'vendor',
            'xref',
            'date_draft',
            'terms',
            'cash_account',
            'prepaid_account',
            'unearned_account',
        ]
        csv_file = forms.FileField(required=False)
        labels = {
            'date_draft': _('Draft Date'),
            'unearned_account': _('Payable Account'),
            'prepaid_account': _('Prepaid Expenses Account')
        }
        widgets = {
            'date_draft': DateInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES,
                'placeholder': _('Bill Date (YYYY-MM-DD)...'),
                'id': 'djl-bill-draft-date-input'
            }),
            'amount_due': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES,
                'placeholder': '$$$',
                'id': 'djl-bill-amount-due-input'}),
            'xref': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES + ' is-large',
                'placeholder': 'External Reference Number...',
                'id': 'djl-bill-xref-input'
            }),
            'terms': Select(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES,
                'id': 'djl-bill-create-terms-select-input'
            }),
            'vendor': Select(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES,
                'id': 'djl-bill-create-vendor-select-input'
            }),

            'cash_account': Select(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES,
                'id': 'djl-bill-cash-account-input'
            }),
            'prepaid_account': Select(
                attrs={
                    'class': DJANGO_LEDGER_FORM_INPUT_CLASSES,
                    'id': 'djl-bill-prepaid-account-input'
                }),
            'unearned_account': Select(
                attrs={
                    'class': DJANGO_LEDGER_FORM_INPUT_CLASSES,
                    'id': 'djl-bill-unearned-account-input'
                }),
        }


class BaseBillModelUpdateForm(BillModelCreateForm):

    def __init__(self,
                 *args,
                 entity_slug,
                 user_model,
                 **kwargs):
        super().__init__(entity_slug=entity_slug, user_model=user_model, *args, **kwargs)
        self.ENTITY_SLUG = entity_slug
        self.USER_MODEL = user_model
        self.BILL_MODEL: BillModel = self.instance

    def save(self, commit=True):
        if commit:
            self.BILL_MODEL.update_state()
            self.instance.migrate_state(
                user_model=self.USER_MODEL,
                entity_slug=self.ENTITY_SLUG,
                raise_exception=False
            )
        super().save(commit=commit)

    class Meta:
        model = BillModel
        fields = [
            'markdown_notes'
        ]
        widgets = {
            'xref': TextInput(attrs={'class': DJANGO_LEDGER_FORM_INPUT_CLASSES,
                                     'placeholder': 'External Reference...'}),
            'timestamp': DateTimeInput(attrs={'class': DJANGO_LEDGER_FORM_INPUT_CLASSES}),
            'amount_due': TextInput(attrs={'class': DJANGO_LEDGER_FORM_INPUT_CLASSES, 'placeholder': '$$$'}),
            'terms': Select(attrs={'class': DJANGO_LEDGER_FORM_INPUT_CLASSES}),
            'bill_status': Select(attrs={'class': DJANGO_LEDGER_FORM_INPUT_CLASSES}),
            'date_paid': DateInput(
                attrs={
                    'class': DJANGO_LEDGER_FORM_INPUT_CLASSES,
                    'placeholder': _('Date (YYYY-MM-DD)...')}
            ),
            'amount_paid': TextInput(
                attrs={
                    'class': DJANGO_LEDGER_FORM_INPUT_CLASSES,
                }),
            'progress': TextInput(attrs={'class': DJANGO_LEDGER_FORM_INPUT_CLASSES}),
            'accrue': CheckboxInput(attrs={'type': 'checkbox'}),
            'paid': CheckboxInput(attrs={'type': 'checkbox'}),
            'cash_account': Select(attrs={'class': DJANGO_LEDGER_FORM_INPUT_CLASSES + ' is-danger'}),
            'prepaid_account': Select(attrs={'class': DJANGO_LEDGER_FORM_INPUT_CLASSES + ' is-danger'}),
            'unearned_account': Select(attrs={'class': DJANGO_LEDGER_FORM_INPUT_CLASSES + ' is-danger'}),
            'markdown_notes': Textarea(attrs={
                'class': 'textarea'
            }),
            'vendor': Select(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES,
                'id': 'djl-bill-create-vendor-select-input'
            }),
        }
        labels = {
            'progress': _('Bill Progress Amount (%)'),
            'accrue': _('Will this Bill be Accrued?'),
            'markdown_notes': _('Notes')
        }

    # def clean(self):
    #     cleaned_data = super().clean()
    #     csv_file = cleaned_data.get("csv_file")
    #     # if csv_file:
    #
    #     return cleaned_data

class DraftBillModelUpdateForm(BaseBillModelUpdateForm):
    class Meta(BaseBillModelUpdateForm.Meta):
        fields = [
            'vendor',
            'terms',
            'xref',
            'markdown_notes'
        ]


class InReviewBillModelUpdateForm(BaseBillModelUpdateForm):
    class Meta(BaseBillModelUpdateForm.Meta):
        fields = [
            'xref',
            'markdown_notes'
        ]


class ApprovedBillModelUpdateForm(BaseBillModelUpdateForm):
    class Meta(BaseBillModelUpdateForm.Meta):
        fields = [
            'amount_paid',
            'markdown_notes'
        ]


class AccruedAndApprovedBillModelUpdateForm(BaseBillModelUpdateForm):
    class Meta(BaseBillModelUpdateForm.Meta):
        fields = [
            'progress',
            'amount_paid',
            'markdown_notes'
        ]


class PaidBillModelUpdateForm(BaseBillModelUpdateForm):
    class Meta(BaseBillModelUpdateForm.Meta):
        fields = [
            'markdown_notes'
        ]


class BillModelConfigureForm(BaseBillModelUpdateForm):
    class Meta(BaseBillModelUpdateForm.Meta):
        fields = [
            'xref',
            'amount_due',
            'amount_paid',
            'date_paid',
            'progress',
            'accrue',
            'cash_account',
            'prepaid_account',
            'unearned_account',
        ]


class BillItemTransactionForm(ModelForm):

    def clean(self):
        cleaned_data = super(BillItemTransactionForm, self).clean()
        itemtxs_model: ItemTransactionModel = self.instance
        if itemtxs_model.po_model is not None:
            quantity = cleaned_data['quantity']
            if quantity > itemtxs_model.po_quantity:
                raise ValidationError(f'Cannot bill more than {itemtxs_model.po_quantity} authorized.')
        return cleaned_data

    class Meta:
        model = ItemTransactionModel
        fields = [
            'item_model',
            'unit_cost',
            'entity_unit',
            'quantity',
        ]
        widgets = {
            'item_model': Select(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES + ' is-small',
            }),
            'entity_unit': Select(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES + ' is-small',
            }),
            'unit_cost': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES + ' is-small',
            }),
            'quantity': TextInput(attrs={
                'class': DJANGO_LEDGER_FORM_INPUT_CLASSES + ' is-small',
            })
        }


class BaseBillItemTransactionFormset(BaseModelFormSet):

    def __init__(self, *args,
                 entity_slug,
                 bill_model: BillModel,
                 user_model,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.USER_MODEL = user_model
        self.BILL_MODEL = bill_model
        self.ENTITY_SLUG = entity_slug

        items_qs = ItemModel.objects.for_bill(
            entity_slug=self.ENTITY_SLUG,
            user_model=self.USER_MODEL
        )

        unit_qs = EntityUnitModel.objects.for_entity(
            entity_slug=self.ENTITY_SLUG,
            user_model=self.USER_MODEL
        )

        for form in self.forms:
            form.fields['item_model'].queryset = items_qs
            form.fields['entity_unit'].queryset = unit_qs

            if not self.BILL_MODEL.can_edit_items():
                form.fields['item_model'].disabled = True
                form.fields['quantity'].disabled = True
                form.fields['unit_cost'].disabled = True
                form.fields['entity_unit'].disabled = True

            instance: ItemTransactionModel = form.instance
            if instance.po_model_id:
                form.fields['item_model'].disabled = True
                form.fields['entity_unit'].disabled = True


def get_bill_itemtxs_formset_class(bill_model: BillModel):
    BillItemTransactionFormset = modelformset_factory(
        model=ItemTransactionModel,
        form=BillItemTransactionForm,
        formset=BaseBillItemTransactionFormset,
        can_delete=True,
        extra=5
    )
    return BillItemTransactionFormset
