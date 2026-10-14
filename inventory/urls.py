from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path(
        'receive/<int:bin_pk>/',
        views.stock_receive,
        name='stock_receive',
    ),
    path(
        'transfer/<int:bin_pk>/',
        views.stock_transfer,
        name='stock_transfer',
    ),
    path(
        'transfers/',
        views.stock_transfer_list,
        name='stock_transfer_list',
    ),
    path(
        'remove/<int:bin_pk>/',
        views.stock_remove,
        name='stock_remove',
    ),
]