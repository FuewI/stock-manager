from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    path(
        'create/',
        views.storage_space_create,
        name='storage_space_create',
    ),
    path(
        '',
        views.storage_space_list,
        name='storage_space_list'
    ),
    path(
        '<int:pk>/',
        views.storage_space_detail,
        name='storage_space_detail',
    ),
    path(
        'bins/<int:pk>/',
        views.storage_bin_detail,
        name='storage_bin_detail',
    ),
    path(
        '<int:pk>/edit/',
        views.storage_space_edit,
        name='storage_space_edit',
    ),
    path(
        '<int:pk>/delete/',
        views.storage_space_delete,
        name='storage_space_delete',
    ),
    path('dashboard/', views.dashboard, name='dashboard'),
    path(
        'bins/<int:pk>/edit/',
        views.storage_bin_edit,
        name='storage_bin_edit',
    ),
]