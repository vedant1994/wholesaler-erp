from django import forms

from .models import Payment

class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment

        fields = [
            "amount",
            "payment_method",
            "reference_number",
            "notes",
        ]

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "Enter payment amount",
                }
            ),

            "reference_number": forms.TextInput(
                attrs={
                    "placeholder": "UPI / bank / cheque reference",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Optional Notes",
                }
            ),
        }