from django.shortcuts import get_object_or_404, redirect, render
from .forms import StorageBinEditForm, StorageSpaceEditForm, StorageSpaceForm
from .models import StorageBin, StorageSpace
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.db.models import Sum
from inventory.models import StockEntry, StockTransfer
from products.models import Product
from inventory.forms import StockEntryForm, StockRemoveForm, StockTransferForm


def storage_space_create(request):
    if request.method == 'POST':
        form = StorageSpaceForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                space = form.save()

                for row in range(1, space.rows + 1):
                    for column in range(1, space.columns + 1):
                        StorageBin.objects.create(
                            storage_space=space,
                            row=row,
                            column=column,
                            capacity=space.default_bin_capacity,
                        )

            return redirect('storage:storage_space_list')
    else:
        form = StorageSpaceForm()

    return render(
        request,
        'storage/storage_space_form.html',
        {'form': form},
    )

def storage_space_list(request):
    spaces = StorageSpace.objects.order_by('name')

    return render(
        request,
        'storage/storage_space_list.html',
        {'spaces': spaces},
    )

def storage_space_detail(request, pk):
    space = get_object_or_404(StorageSpace, pk=pk)
    remove_form = None

    bins = space.bins.select_related(
        'stock_entry__product',
    ).order_by('row', 'column')

    selected_bin = None
    selected_id = request.GET.get('bin', '')

    if selected_id.isdigit():
        selected_bin = get_object_or_404(bins, pk=int(selected_id))

    transfer_form = None
    receive_form = None

    if selected_bin is not None:
        source_entry = StockEntry.objects.filter(bin=selected_bin).first()

        if source_entry is not None:
            remove_form = StockRemoveForm(source_entry=source_entry)
            transfer_form = StockTransferForm(source_entry=source_entry)
            receive_form = StockEntryForm(instance=source_entry)
        else:
            receive_form = StockEntryForm(
                instance=StockEntry(bin=selected_bin),
            )

    return render(
        request,
        'storage/storage_space_detail.html',
        {
            'space': space,
            'bins': bins,
            'selected_bin': selected_bin,
            'transfer_form': transfer_form,
            'receive_form': receive_form,
            'remove_form': remove_form,
        },
    )

def storage_bin_detail(request, pk):
    bin = get_object_or_404(
        StorageBin.objects.select_related('storage_space'),
        pk=pk,
    )

    return render(
        request,
        'storage/storage_bin_detail.html',
        {'bin': bin},
    )

def storage_space_edit(request, pk):
    space = get_object_or_404(StorageSpace, pk=pk)

    if request.method == 'POST':
        form = StorageSpaceEditForm(request.POST, instance=space)

        if form.is_valid():
            form.save()
            return redirect('storage:storage_space_detail', pk=space.pk)
    else:
        form = StorageSpaceEditForm(instance=space)

    return render(
        request,
        'storage/storage_space_form.html',
        {'form': form, 'is_edit': True},
    )

def storage_space_delete(request, pk):
    space = get_object_or_404(StorageSpace, pk=pk)
    error = None

    if request.method == 'POST':
        try:
            space.delete()
        except ProtectedError:
            error = (
                'This storage space contains stock. '
                'Remove or transfer all stock before deleting it.'
            )
        else:
            return redirect('storage:storage_space_list')

    return render(
        request,
        'storage/storage_space_confirm_delete.html',
        {'space': space, 'error': error},
    )

def dashboard(request):
    total_items = (
        StockEntry.objects.aggregate(total=Sum('quantity'))['total'] or 0
    )

    recent_transfers = StockTransfer.objects.select_related(
        'product',
        'source_bin__storage_space',
        'destination_bin__storage_space',
    ).order_by('-created_at', '-pk')[:5]

    return render(
        request,
        'storage/dashboard.html',
        {
            'storage_count': StorageSpace.objects.count(),
            'product_count': Product.objects.count(),
            'total_items': total_items,
            'recent_transfers': recent_transfers,
        },
    )

def storage_bin_edit(request, pk):
    bin = get_object_or_404(StorageBin, pk=pk)

    if request.method == 'POST':
        form = StorageBinEditForm(request.POST, instance=bin)

        if form.is_valid():
            form.save()
            return redirect('storage:storage_bin_detail', pk=bin.pk)
    else:
        form = StorageBinEditForm(instance=bin)

    return render(
        request,
        'storage/storage_bin_form.html',
        {'form': form, 'bin': bin},
    )