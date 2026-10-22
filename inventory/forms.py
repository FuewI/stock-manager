from django import forms
from .models import StockEntry
from storage.models import StorageBin


class StockEntryForm(forms.ModelForm):
    class Meta:
        model = StockEntry
        fields = ['product', 'quantity']

        labels = {
            'product': 'Product to store',
            'quantity': 'Quantity to add',
        }

        help_texts = {
            'quantity': 'Enter the number of additional items.',
        }

        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

        error_messages = {
            'product': {
                'required': 'Please select a product.',
            },
            'quantity': {
                'required': 'Please enter a quantity.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_quantity = (
            self.instance.quantity if self.instance.pk else 0
        )
        self.initial['quantity'] = None

        if self.instance.pk:
            self.fields['product'].disabled = True

    def clean_quantity(self):
        quantity_to_add = self.cleaned_data['quantity']

        if quantity_to_add < 1:
            raise forms.ValidationError('Please add at least one item.')

        return self.current_quantity + quantity_to_add

class DestinationBinChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, bin):
        available_items = (
            bin.remaining_capacity // self.product.space_per_unit
        )

        return f'{bin} — room for {available_items} more'

class StockTransferForm(forms.Form):
    destination_bin = DestinationBinChoiceField(
        queryset=StorageBin.objects.none(),
        label='Move to',
        empty_label='Select a destination bin',
    )
    quantity = forms.IntegerField(
        min_value=1,
        label='Quantity to move',
        widget=forms.NumberInput(attrs={'min': 1}),
    )

    def __init__(self, *args, source_entry, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_entry = source_entry

        product = source_entry.product
        destination_field = self.fields['destination_bin']
        destination_field.product = product

        candidates = (
            StorageBin.objects
            .exclude(pk=source_entry.bin_id)
            .select_related('storage_space', 'stock_entry__product')
            .order_by('storage_space__name', 'row', 'column')
        )

        available_ids = []

        for bin in candidates:
            try:
                existing_entry = bin.stock_entry
            except StockEntry.DoesNotExist:
                existing_entry = None

            compatible = (
                existing_entry is None
                or existing_entry.product_id == product.pk
            )

            if compatible and bin.remaining_capacity >= product.space_per_unit:
                available_ids.append(bin.pk)

        destination_field.queryset = candidates.filter(
            pk__in=available_ids,
        )
        destination_field.help_text = (
            'Only compatible positions with room for at least one item '
            'are listed.'
        )

    def clean(self):
        cleaned_data = super().clean()
        destination = cleaned_data.get('destination_bin')
        quantity = cleaned_data.get('quantity')

        if quantity is None:
            return cleaned_data

        if quantity > self.source_entry.quantity:
            self.add_error(
                'quantity',
                f'Only {self.source_entry.quantity} items are available.',
            )

        if destination is None:
            return cleaned_data

        destination_entry = StockEntry.objects.filter(
            bin=destination,
        ).first()

        if (
            destination_entry is not None
            and destination_entry.product_id != self.source_entry.product_id
        ):
            self.add_error(
                'destination_bin',
                'This bin contains a different product.',
            )
            return cleaned_data

        existing_quantity = (
            destination_entry.quantity if destination_entry else 0
        )
        required_space = (
            (existing_quantity + quantity)
            * self.source_entry.product.space_per_unit
        )

        if required_space > destination.capacity:
            self.add_error(
                'destination_bin',
                'The destination does not have enough capacity.',
            )

        return cleaned_data

class StockRemoveForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        label='Quantity to remove',
        help_text='For sales, damage, or an inventory correction.',
        widget=forms.NumberInput(attrs={'min': 1}),
    )

    def __init__(self, *args, source_entry, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_entry = source_entry

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if quantity > self.source_entry.quantity:
            raise forms.ValidationError(
                f'You can remove at most '
                f'{self.source_entry.quantity} items.'
            )

        return quantity