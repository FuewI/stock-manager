from django.shortcuts import get_object_or_404, redirect, render
from .forms import CategoryForm, ProductForm
from .models import Category, Product
from django.db.models.deletion import ProtectedError
from django.db.models import Q


def product_list(request):
    products = Product.objects.prefetch_related(
    'stock_entries__bin__storage_space',
)
    categories = Category.objects.order_by('name')

    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'name')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(sku__icontains=query)
        )

    if selected_category.isdigit():
        products = products.filter(
            categories__pk=int(selected_category),
        )

    sort_options = {
        'name': 'name',
        'name_desc': '-name',
        'space': 'space_per_unit',
    }
    products = products.order_by(
        sort_options.get(sort, 'name'),
        'pk',
    )

    return render(
        request,
        'products/product_list.html',
        {
            'products': products,
            'categories': categories,
            'query': query,
            'selected_category': selected_category,
            'sort': sort,
        },
    )


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('products:product_list')
    else:
        form = ProductForm()

    return render(
        request,
        'products/product_form.html',
        {'form': form},
    )

def category_list(request):
    categories = Category.objects.order_by('name')

    return render(
        request,
        'products/category_list.html',
        {'categories': categories},
    )


def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('products:category_list')
    else:
        form = CategoryForm()

    return render(
        request,
        'products/category_form.html',
        {'form': form},
    )

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        'products/product_form.html',
        {'form': form, 'is_edit': True},
    )

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    stock_entries = product.stock_entries.select_related(
        'bin__storage_space',
    ).order_by('bin__storage_space__name', 'bin__row', 'bin__column')

    return render(
        request,
        'products/product_detail.html',
        {
            'product': product,
            'stock_entries': stock_entries,
        },
    )

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    error = None

    if request.method == 'POST':
        try:
            product.delete()
        except ProtectedError:
            error = (
                'This product still has stock in storage bins. '
                'Remove its stock before deleting it.'
            )
        else:
            return redirect('products:product_list')

    return render(
        request,
        'products/product_confirm_delete.html',
        {'product': product, 'error': error},
    )