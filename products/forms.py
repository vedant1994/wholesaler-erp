from django import forms
from .models import Product, Stock

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            "name",
            "sku",
            "category",
            "unit",
            "description",
        ]

class StockForm(forms.ModelForm):

    class Meta:
        model = Stock

        fields=[
            "product",
            "quantity",
            "purchase_price",
            "selling_price",
            "mrp",
            "supplier",
            "batch_number",
            "expiry_date",
            "minimum_stock",
        ]

        widget = {
            "expiry_date": forms.DateInput(
                attrs = {"type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):

        wholesaler = kwargs.pop("wholesaler", None)

        super().__init__(*args, **kwargs)

        if wholesaler:
            self.fields["product"].queryset = Product.objects.filter(
                wholesaler = wholesaler
            )