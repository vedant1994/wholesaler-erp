# 🏬 Wholesaler ERP — Enterprise Supply Chain & Billing Platform

![Django](https://img.shields.io/badge/Django-6.1-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-3.14-red?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Dual_Web_%2B_REST_API-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **Wholesaler ERP** is a full-stack, enterprise-grade B2B & B2C Resource Planning platform engineered for modern FMCG wholesalers, distributors, and retail shop owners. It bridges the gap between suppliers and retailers with **FEFO inventory batch management**, **automated GST invoice calculation**, **double-entry financial ledgers**, **smart order fulfillment**, and **dual Web HTML + REST API interfaces**.

---

## 💡 Why Wholesaler ERP? (The Problem & Solution)

Traditional supply chains face friction at every step:
- **Inventory Waste**: Perishable stock expires on shelves due to manual stock rotation failures.
- **Order Deadlocks**: Orders get accepted without knowing if stock is actually available.
- **Accounting Errors**: Manual credit/debit tracking leads to payment disputes between wholesalers and retailers.

**Wholesaler ERP solves all three**:
1. 📦 **Automated FEFO (First Expiring, First Out) Inventory Engine**: Stock is automatically deducted from batches closest to expiry.
2. ⚡ **Smart Order Lifecycle with Fallback**: Orders auto-check inventory; if stock is temporarily depleted, orders safely transition into `WAITING_FOR_STOCK` and auto-fulfill the second new stock arrives.
3. 📒 **Automated Ledger Bookkeeping**: Generates `DEBIT` entries on invoice creation and `CREDIT` entries on payment receipt.

---

## 🚀 Key Modules & System Architecture

The platform consists of **7 interconnected micro-apps**, accessible via both **Web HTML templates** and **REST APIs**:

```
                              ┌────────────────────────┐
                              │     Wholesaler ERP     │
                              └───────────┬────────────┘
                                          │
    ┌──────────────┬──────────────┬───────┴──────┬──────────────┬──────────────┬──────────────┐
    │              │              │              │              │              │              │
┌───┴────┐   ┌─────┴────┐   ┌─────┴────┐   ┌─────┴────┐   ┌─────┴────┐   ┌─────┴────┐   ┌─────┴────┐
│Accounts│   │ Products │   │  Orders  │   │ Billing  │   │ Payments │   │Customers │   │ Shipping │
└────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### 🔐 1. Accounts & Multi-Role Authentication
- Dual user personas: **WHOLESALER** (Suppliers) vs. **RETAILER** (Shop Owners).
- Real-time **Dashboard Stats Engine** calculating total sales, unpaid balances, low stock counts, and expiring items.
- Live in-app notifications system.

### 📦 2. Products & FEFO Batch Inventory
- Multi-batch tracking (`batch_number`, `purchase_price`, `selling_price`, `mrp`, `expiry_date`, `minimum_stock`).
- Real-time stock status computation: `LOW_STOCK`, `SOON_EXPIRING` (within 30 days), `EXPIRED`, `GOOD`.
- Automatic synchronization between Wholesaler stock and Retailer inventory upon order fulfillment.

### 🛒 3. B2B Order Management
- Order lifecycle: `PENDING` $\rightarrow$ `ACCEPTED` $\rightarrow$ `PROCESSING` $\rightarrow$ `SHIPPED` $\rightarrow$ `DELIVERED` (or `REJECTED`/`CANCELLED`).
- Automated stock allocation using `FEFO` algorithm locked with `@transaction.atomic` and `select_for_update()`.
- Safe `WAITING_FOR_STOCK` fallback state when inventory is insufficient.

### 🧾 4. Billing & Invoice Engine
- **B2B Invoices**: Auto-generated from fulfilled orders with itemized GST rates (5%, 12%, 18%) and unique sequential invoice numbering (`INV-YYYY-XXXXXX`).
- **PDF & QR Code Generation**: Downloadable PDF invoices with QR code verification links.
- **B2C Retailer POS Invoices**: Quick point-of-sale customer billing with **CGST (9%)**, **SGST (9%)**, and automated half-up rounding.

### 💳 5. Financial Ledgers & Payments
- Payment support for `CASH`, `UPI`, `BANK_TRANSFER`, `CHEQUE`, `CARD`, and `OTHER`.
- Double-entry accounting ledger: `DEBIT` entries logged when invoices are issued, `CREDIT` entries logged when payments are received.
- Partial payment tracking (`UNPAID` $\rightarrow$ `PARTIALLY_PAID` $\rightarrow$ `PAID`).

### 👥 6. Customer CRM
- Retailer customer contact profiles with GSTIN tracking for B2C billing.

### 🚚 7. Shipping & Logistics
- Shipment tracking (`courier`, `tracking_number`, `shipping_date`, `expected_delivery`, `status`).

---

## ⚡ Core Business Algorithms & Smart Logic

### 1. FEFO (First Expiring, First Out) Stock Allocation
```python
# From orders/services.py
stocks = list(
    Stock.objects
    .select_for_update()
    .filter(product=item.product, quantity__gt=0)
    .filter(Q(expiry_date__isnull=True) | Q(expiry_date__gte=today))
    .order_by("expiry_date", "created_at") # FEFO Order
)
```
> *Why it matters*: Prioritizes dispatching stock closest to expiration, drastically reducing inventory waste for wholesalers.

### 2. Transaction Lock Safety (`@transaction.atomic` + `select_for_update()`)
> *Why it matters*: Prevents race conditions during flash sales or simultaneous retailer orders. Multiple orders for the same stock batch are queued cleanly by the database lock.

---

## 🤝 Development Approach & AI Pair Programming

This project was conceptualized, architected, and built by **the developer** after completing in-depth learning of software engineering principles, Django web architecture, and ERP supply-chain workflows.

**AI (Antigravity AI)** was utilized purely as a **secondary coding assistant & pair programmer** for guidance, code refactoring, REST API boilerplate generation, and syntax validation — ensuring the developer's core vision and design patterns were implemented seamlessly.

```
┌──────────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────────┐
│  1. Human Architecture   │ ──> │   2. AI Pair Assistance  │ ──> │   3. Quality & Testing   │
│ Concept design, business │     │ Standardizing REST APIs, │     │ AST syntax validation &  │
│ workflows & database     │     │ serializers & endpoint   │     │ dual web + API browser   │
│ schema by Developer      │     │  routing under guidance  │     │       integration        │
└──────────────────────────┘     └──────────────────────────┘     └──────────────────────────┘
```

### Key Highlights of the Developer + AI Synergy:
1. **Developer-Led Architecture**: All core domain concepts (FEFO stock batching, double-entry accounting ledgers, multi-role Wholesaler/Retailer permissions, and GST tax rules) were researched, designed, and conceptualized by the developer.
2. **AI-Assisted Pair Programming**: AI served as an intelligent assistant to help write boilerplate REST serializers, streamline API endpoint routing, and ensure full backward compatibility with the original web app.
3. **Refactoring & Code Quality**: AI assisted in enforcing robust transaction locks (`@transaction.atomic`), automated test syntax verification, and generating detailed technical documentation.

---

## 🛠️ Tech Stack & Dependencies

| Layer | Technology |
| :--- | :--- |
| **Framework** | Django 6.1 |
| **REST API** | Django REST Framework (DRF) 3.14 |
| **Language** | Python 3.14 |
| **Database** | SQLite (Production-ready for PostgreSQL / MySQL) |
| **PDF Generation** | ReportLab |
| **QR Code Engine** | `qrcode`, `io`, `base64` |
| **Authentication** | Session & Basic Auth (`django.contrib.auth`) |

---

## 🌐 API Endpoint Cheatsheet

All APIs are available under the `/api/` namespace. Opening `http://127.0.0.1:8000/api/` in your browser opens the **Interactive Browsable API Directory**.

| Module | HTTP Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Accounts** | `POST` | `/api/accounts/register/` | Register Wholesaler / Retailer |
| | `POST` | `/api/accounts/login/` | Authenticate user |
| | `GET/PUT` | `/api/accounts/profile/` | Business profile details |
| | `GET` | `/api/accounts/dashboard-stats/` | Real-time analytics dashboard |
| **Products** | `GET / POST` | `/api/products/` | Product catalog CRUD |
| | `GET / POST` | `/api/products/stock/` | Stock batch management (FEFO filters) |
| **Orders** | `GET / POST` | `/api/orders/` | Place & view B2B orders |
| | `PATCH` | `/api/orders/<id>/` | Accept/Reject order status |
| | `POST` | `/api/orders/<id>/fulfill/` | Retry stock fulfillment |
| **Billing** | `GET` | `/api/billing/invoices/` | List B2B invoices |
| | `POST` | `/api/billing/invoices/generate/<id>/` | Generate invoice from order |
| | `GET` | `/api/billing/invoices/<id>/pdf/` | Download Invoice PDF |
| | `GET / POST` | `/api/billing/customer-invoices/` | Retailer POS Customer Billing |
| **Payments** | `GET / POST` | `/api/payments/` | Record invoice payment |
| | `GET` | `/api/payments/ledger/` | Double-entry financial ledger |
| **Customers** | `GET / POST` | `/api/customers/` | Customer CRM CRUD |
| **Shipping** | `GET / POST` | `/api/shipping/` | Track shipments & logistics |

---

## 🚀 Quick Run Guide

### 1. Clone the repository
```bash
git clone https://github.com/your-username/wholesaler-erp.git
cd wholesaler-erp/wholsaler_erp
```

### 2. Install dependencies & run migrations
```bash
pip install django djangorestframework reportlab qrcode pillow
python manage.py migrate
```

### 3. Create a superuser / test account
```bash
python manage.py createsuperuser
```

### 4. Start the development server
```bash
python manage.py runserver
```

- 🌐 **Web Portal**: Visit `http://127.0.0.1:8000/`
- 📡 **Interactive REST API**: Visit `http://127.0.0.1:8000/api/`

---

<p center>
  Crafted with ❤️ by the Developer, with AI assistance from <b>Antigravity AI</b>.
</p>
