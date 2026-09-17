from django.urls import path
from .views import add_product, product_list, edit_product, delete_product, add_stock, stock_list, edit_stock, delete_stock, low_stock_list, expiry_list

urlpatterns = [
    path("add/", add_product, name="add_product"),
    path("edit/<int:product_id>/", edit_product, name="edit_product"),
    path("delete/<int:product_id>/", delete_product, name="delete_product"),
    path("stock/add/", add_stock, name="add_stock"),
    path("stock/<int:stock_id>/", edit_stock, name="edit_stock"),
    path("stock/delete/<int:stock_id>/", delete_stock, name="delete_stock"),
    path("stock/", stock_list, name="stock_list"),
    path("stock/low/", low_stock_list, name="low_stock_list"),
    path("stock/expiry/", expiry_list, name="expiry_list"),
    path("", product_list, name="product_list"),
]