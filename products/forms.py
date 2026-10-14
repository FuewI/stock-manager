from django import forms
from .models import Category, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'sku',
            'description',
            'space_per_unit',
            'categories',
        ]

        labels = {
            'name': 'Product name',
            'sku': 'Product code (SKU)',
            'space_per_unit': 'Space per item',
        }

        help_texts = {
            'sku': 'A unique code identifying this product.',
            'space_per_unit': 'Storage units occupied by one item.',
            'categories': 'Optional. Select categories for this product.',
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. USB keyboard',
            }),
            'sku': forms.TextInput(attrs={
                'placeholder': 'e.g. KEYBOARD-001',
            }),
            'description': forms.Textarea(attrs={'rows': 3}),
            'space_per_unit': forms.NumberInput(attrs={'min': 1}),
            'categories': forms.CheckboxSelectMultiple(),
        }

        error_messages = {
            'name': {
                'required': 'Please enter a product name.',
            },
            'sku': {
                'required': 'Please enter a product code.',
                'unique': 'A product with this code already exists.',
            },
        }

    def clean_space_per_unit(self):
        space_per_unit = self.cleaned_data['space_per_unit']

        if self.instance.pk:
            stock_entries = self.instance.stock_entries.select_related(
                'bin__storage_space',
            )

            for entry in stock_entries:
                required_space = entry.quantity * space_per_unit

                if required_space > entry.bin.capacity:
                    raise forms.ValidationError(
                        f'This size would exceed capacity in '
                        f'{entry.bin.storage_space.name}, '
                        f'row {entry.bin.row}, column {entry.bin.column}. '
                        f'The stored quantity requires {required_space} '
                        f'units, but capacity is {entry.bin.capacity}.'
                    )

        return space_per_unit

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

        labels = {
            'name': 'Category name',
            'description': 'Description',
        }

        help_texts = {
            'description': 'Optional. Describe what belongs in this category.',
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Electronics',
            }),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

        error_messages = {
            'name': {
                'required': 'Please enter a category name.',
                'unique': 'A category with this name already exists.',
                'max_length': 'The name cannot exceed 100 characters.',
            },
        }