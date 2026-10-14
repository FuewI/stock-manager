import django.core.validators
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models



class StorageSpace(models.Model):
    name = models.CharField(max_length=100)
    space_type = models.CharField(
        max_length=20,
        choices=[('warehouse', 'Warehouse'), ('store', 'Store')],
    )
    rows = models.PositiveIntegerField(
        validators=[django.core.validators.MinValueValidator(1)],
    )
    columns = models.PositiveIntegerField(
        validators=[django.core.validators.MinValueValidator(1)],
    )
    default_bin_capacity = models.PositiveIntegerField(
        validators=[django.core.validators.MinValueValidator(1)],
    )

    def __str__(self):
        return f"{self.name} ({self.space_type})"


class StorageBin(models.Model):
    storage_space = models.ForeignKey(
        StorageSpace,
        on_delete=models.CASCADE,
        related_name='bins',
    )
    row = models.PositiveIntegerField(
        validators=[django.core.validators.MinValueValidator(1)],
    )
    column = models.PositiveIntegerField(
        validators=[django.core.validators.MinValueValidator(1)],
    )
    capacity = models.PositiveIntegerField(
        validators=[django.core.validators.MinValueValidator(1)],
    )

    class Meta:
        unique_together = ('storage_space', 'row', 'column')

    @property
    def used_capacity(self):
        try:
            stock_entry = self.stock_entry
        except ObjectDoesNotExist:
            return 0

        return stock_entry.used_capacity

    @property
    def remaining_capacity(self):
        return self.capacity - self.used_capacity

    def __str__(self):
        return f"Bin ({self.row}, {self.column}) in {self.storage_space.name}"

    def clean(self):
        super().clean()

        if not self.storage_space_id:
            return  # Skip validation if storage_space is not set

        errors = {}

        if self.row is not None and self.row > self.storage_space.rows:
            errors['row'] = (
                f'Row cannot exceed {self.storage_space.rows} '
                f'for this storage space.'
            )
        if self.column is not None and self.column > self.storage_space.columns:
            errors['column'] = (
                f'Column cannot exceed {self.storage_space.columns} '
                f'for this storage space.'
            )

        if errors:
            raise ValidationError(errors)