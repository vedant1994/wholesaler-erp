from django import forms

class CreateOrderForm(forms.Form):

    quantity = forms.DecimalField(
        min_value=0.01,
        max_digits=12,
        decimal_places=2
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea
    )