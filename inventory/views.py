from django.shortcuts import get_object_or_404, redirect, render
from storage.models import StorageBin
from django.db import transaction
from .forms import StockRemoveForm, StockEntryForm, StockTransferForm
from .models import StockEntry, StockTransfer


def stock_receive(request, bin_pk):
    bin = get_object_or_404(StorageBin, pk=bin_pk)

    stock_entry = StockEntry.objects.filter(bin=bin).first()

    if stock_entry is None:
        stock_entry = StockEntry(bin=bin)

    current_quantity = stock_entry.quantity if stock_entry.pk else 0

    if request.method == 'POST':
        form = StockEntryForm(request.POST, instance=stock_entry)

        if form.is_valid():
            form.save()
            return redirect('storage:storage_bin_detail', pk=bin.pk)
    else:
        form = StockEntryForm(instance=stock_entry)

    return render(
        request,
        'inventory/stock_receive.html',
        {
            'form': form,
            'bin': bin,
            'current_quantity': current_quantity,
        },
    )

def stock_transfer(request, bin_pk):
    with transaction.atomic():
        source_entry = get_object_or_404(
            StockEntry.objects.select_for_update(),
            bin_id=bin_pk,
        )

        if request.method == 'POST':
            form = StockTransferForm(
                request.POST,
                source_entry=source_entry,
            )

            if form.is_valid():
                destination = form.cleaned_data['destination_bin']
                quantity = form.cleaned_data['quantity']

                destination_entry = StockEntry.objects.filter(
                    bin=destination,
                ).first()

                if destination_entry is None:
                    destination_entry = StockEntry(
                        product=source_entry.product,
                        bin=destination,
                        quantity=quantity,
                    )
                else:
                    destination_entry.quantity += quantity

                destination_entry.full_clean()
                destination_entry.save()

                StockTransfer.objects.create(
                    product=source_entry.product,
                    source_bin=source_entry.bin,
                    destination_bin=destination,
                    quantity=quantity,
                )

                source_entry.quantity -= quantity

                if source_entry.quantity == 0:
                    source_entry.delete()
                else:
                    source_entry.save()

                return redirect(
                    'storage:storage_bin_detail',
                    pk=bin_pk,
                )
        else:
            form = StockTransferForm(source_entry=source_entry)

        return render(
            request,
            'inventory/stock_transfer.html',
            {
                'form': form,
                'source_entry': source_entry,
            },
        )

def stock_transfer_list(request):
    transfers = StockTransfer.objects.select_related(
        'product',
        'source_bin__storage_space',
        'destination_bin__storage_space',
    ).order_by('-created_at', '-pk')

    return render(
        request,
        'inventory/stock_transfer_list.html',
        {'transfers': transfers},
    )

def stock_remove(request, bin_pk):
    with transaction.atomic():
        source_entry = get_object_or_404(
            StockEntry.objects.select_for_update(),
            bin_id=bin_pk,
        )

        if request.method == 'POST':
            form = StockRemoveForm(
                request.POST,
                source_entry=source_entry,
            )

            if form.is_valid():
                source_entry.quantity -= form.cleaned_data['quantity']

                if source_entry.quantity == 0:
                    source_entry.delete()
                else:
                    source_entry.save()

                return redirect(
                    'storage:storage_bin_detail',
                    pk=bin_pk,
                )
        else:
            form = StockRemoveForm(source_entry=source_entry)

        return render(
            request,
            'inventory/stock_remove.html',
            {'form': form, 'source_entry': source_entry},
        )