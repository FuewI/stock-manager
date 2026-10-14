from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError


class StockEntry(models.Model):
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='stock_entries',
    )
    bin = models.OneToOneField(
        'storage.StorageBin',
        on_delete=models.PROTECT,
        related_name='stock_entry',
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    @property
    def used_capacity(self):
        return self.quantity * self.product.space_per_unit

    def __str__(self):
        return f"{self.product} — {self.bin} — {self.quantity} units"

    def clean(self):
        super().clean()

        if (
            not self.product_id
            or not self.bin_id
            or self.quantity is None
        ):
            return

        required_space = self.quantity * self.product.space_per_unit

        if required_space > self.bin.capacity:
            max_quantity = self.bin.capacity // self.product.space_per_unit

            raise ValidationError({
                'quantity': (
                    f'This bin can hold at most {max_quantity} units '
                    f'of this product. Your quantity requires '
                    f'{required_space} storage units, but the bin '
                    f'capacity is {self.bin.capacity}.'
                )
            })

class StockTransfer(models.Model):
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='transfers',
    )
    source_bin = models.ForeignKey(
        'storage.StorageBin',
        on_delete=models.PROTECT,
        related_name='outgoing_transfers',
    )
    destination_bin = models.ForeignKey(
        'storage.StorageBin',
        on_delete=models.PROTECT,
        related_name='incoming_transfers',
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'{self.quantity} × {self.product.name}: '
            f'{self.source_bin} → {self.destination_bin}'
        )