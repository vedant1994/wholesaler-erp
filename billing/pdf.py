from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .models import Invoice


def generate_invoice_pdf(invoice_id, wholesaler):

    invoice = (
        Invoice.objects
        .select_related(
            "order",
            "wholesaler",
            "retailer",
        )
        .prefetch_related(
            "items__product"
        )
        .get(
            id=invoice_id,
            wholesaler=wholesaler
        )
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=10,
    )

    right_style = ParagraphStyle(
        "Right",
        parent=styles["Normal"],
        alignment=TA_RIGHT,
    )

    story = []

    # --------------------------------
    # HEADER
    # --------------------------------

    story.append(
        Paragraph(
            "TAX INVOICE",
            title_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Invoice Number:</b> {invoice.invoice_number}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Date:</b> "
            f"{invoice.invoice_date.strftime('%d %b %Y, %I:%M %p')}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 10))

    # --------------------------------
    # SELLER / BUYER
    # --------------------------------

    seller = (
        f"<b>SELLER</b><br/>"
        f"<b>{invoice.wholesaler.business_name}</b><br/>"
        f"{invoice.wholesaler.address}<br/>"
        f"{invoice.wholesaler.city}, "
        f"{invoice.wholesaler.state} - "
        f"{invoice.wholesaler.pincode}<br/>"
        f"Phone: {invoice.wholesaler.phone}"
    )

    if invoice.wholesaler.gst_number:
        seller += (
            f"<br/>GSTIN: "
            f"{invoice.wholesaler.gst_number}"
        )

    buyer = (
        f"<b>BUYER</b><br/>"
        f"<b>{invoice.retailer.shop_name}</b><br/>"
        f"Owner: {invoice.retailer.owner_name}<br/>"
        f"{invoice.retailer.address}<br/>"
        f"{invoice.retailer.city}, "
        f"{invoice.retailer.state} - "
        f"{invoice.retailer.pincode}<br/>"
        f"Phone: {invoice.retailer.phone}"
    )

    if invoice.retailer.gst_number:
        buyer += (
            f"<br/>GSTIN: "
            f"{invoice.retailer.gst_number}"
        )

    business_table = Table(
        [
            [
                Paragraph(seller, styles["Normal"]),
                Paragraph(buyer, styles["Normal"]),
            ]
        ],
        colWidths=[85 * mm, 85 * mm],
    )

    business_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    story.append(business_table)

    story.append(Spacer(1, 15))

    # --------------------------------
    # ITEMS
    # --------------------------------

    item_data = [
        [
            "#",
            "Product",
            "Qty",
            "Rate",
            "GST %",
            "Tax",
            "Total",
        ]
    ]

    for index, item in enumerate(invoice.items.all(), start=1):

        item_data.append([
            str(index),
            item.product.name,
            str(item.quantity),
            f"₹{item.price_per_unit}",
            f"{item.tax_rate}%",
            f"₹{item.tax_amount}",
            f"₹{item.total_price}",
        ])

    item_table = Table(
        item_data,
        colWidths=[
            10 * mm,
            55 * mm,
            20 * mm,
            25 * mm,
            20 * mm,
            20 * mm,
            25 * mm,
        ],
        repeatRows=1,
    )

    item_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(item_table)

    story.append(Spacer(1, 15))

    # --------------------------------
    # TOTALS
    # --------------------------------

    totals_data = [
        ["Subtotal", f"₹{invoice.subtotal}"],
        ["Discount", f"₹{invoice.discount}"],
        ["GST / Tax", f"₹{invoice.tax_amount}"],
        ["Grand Total", f"₹{invoice.grand_total}"],
    ]

    totals_table = Table(
        totals_data,
        colWidths=[120 * mm, 50 * mm],
    )

    totals_table.setStyle(
        TableStyle([
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("LINEABOVE", (0, 3), (-1, 3), 1),
            ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
            ("FONTSIZE", (0, 3), (-1, 3), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(totals_table)

    story.append(Spacer(1, 20))

    # --------------------------------
    # PAYMENT STATUS
    # --------------------------------

    story.append(
        Paragraph(
            f"<b>Payment Status:</b> "
            f"{invoice.get_status_display()}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "This is a computer-generated invoice.",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            "Thank you for your business.",
            styles["Normal"]
        )
    )

    # Generate PDF
    document.build(story)

    buffer.seek(0)

    return buffer