from django import forms
from .models import StorageBin, StorageSpace


class StorageSpaceForm(forms.ModelForm):
    class Meta:
        model = StorageSpace

        fields = [
            'name',
            'space_type',
            'rows',
            'columns',
            'default_bin_capacity',
        ]

        labels = {
            'name': 'Storage name',
            'space_type': 'Storage type',
            'rows': 'Number of rows',
            'columns': 'Number of columns',
            'default_bin_capacity': 'Capacity per bin',
        }

        help_texts = {
            'rows': 'How many rows your storage grid contains.',
            'columns': 'How many positions each row contains.',
            'default_bin_capacity': (
                'Storage units available in each bin initially.'
            ),
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Warehouse A',
            }),
            'rows': forms.NumberInput(attrs={'min': 1}),
            'columns': forms.NumberInput(attrs={'min': 1}),
            'default_bin_capacity': forms.NumberInput(attrs={'min': 1}),
        }

        error_messages = {
            'name': {
                'required': 'Please enter a name for your storage space.',
                'max_length': 'The name cannot exceed 100 characters.',
            },
            'space_type': {
                'required': 'Please choose a warehouse or store.',
                'invalid_choice': 'Please select a valid storage type.',
            },
        }

class StorageSpaceEditForm(StorageSpaceForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in ['rows', 'columns', 'default_bin_capacity']:
            self.fields[field_name].disabled = True
            self.fields[field_name].help_text = (
                'This setting cannot be changed after creation.'
            )

class StorageBinEditForm(forms.ModelForm):
    class Meta:
        model = StorageBin
        fields = ['capacity']

        labels = {
            'capacity': 'Bin capacity',
        }

        help_texts = {
            'capacity': 'Total storage units available in this bin.',
        }

        widgets = {
            'capacity': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_capacity(self):
        capacity = self.cleaned_data['capacity']
        used_capacity = self.instance.used_capacity

        if capacity < used_capacity:
            raise forms.ValidationError(
                f'This bin already uses {used_capacity} storage units. '
                f'Capacity cannot be lower than that.'
            )

        return capacity