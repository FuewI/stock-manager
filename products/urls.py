from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('categories/', views.category_list, name='category_list',),
    path('categories/create/', views.category_create, name='category_create',),
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
]