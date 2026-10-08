from decimal import Decimal

from django.db.models import Sum, Q

from .models import LedgerEntry

def get_ledger_summary(wholesaler, retailer):

    debit = (
        LedgerEntry.objects
        .filter(
            wholesaler = wholesaler,
            retailer = retailer,
            entry_type="DEBIT"
        )
        .aggregate(
            total=Sum("amount")
        )
        ["total"]
        or Decimal("0.00")
    )

    credit = (
        LedgerEntry.objects
        .filter(
            wholesaler = wholesaler,
            retailer = retailer,
            entry_type = "CREDIT"
        )
        .aggregate(
            total=Sum("amount")
        )
        ["total"]
        or Decimal("0.00")
    )

    outstanding = debit - credit

    return {
        "total_debit": debit,
        "total_credit": credit,
        "outstanding": outstanding,
    }