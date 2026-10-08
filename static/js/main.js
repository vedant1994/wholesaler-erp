// =====================================================
// ERP Main JS — main.js
// =====================================================

// --- Sidebar Toggle ---
document.addEventListener('DOMContentLoaded', function () {

  const sidebar = document.getElementById('sidebar');
  const mainArea = document.getElementById('mainArea');
  const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
  const mobileOverlay = document.getElementById('mobileOverlay');
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');

  function isMobile() { return window.innerWidth <= 768; }

  if (sidebarToggleBtn) {
    sidebarToggleBtn.addEventListener('click', function () {
      if (isMobile()) {
        sidebar.classList.remove('mobile-open');
        mobileOverlay.classList.remove('active');
      } else {
        sidebar.classList.toggle('collapsed');
        mainArea.classList.toggle('sidebar-collapsed');
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
      }
    });
  }

  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', function () {
      sidebar.classList.toggle('mobile-open');
      mobileOverlay.classList.toggle('active');
    });
  }

  if (mobileOverlay) {
    mobileOverlay.addEventListener('click', function () {
      sidebar.classList.remove('mobile-open');
      mobileOverlay.classList.remove('active');
    });
  }

  // Restore sidebar state from localStorage
  if (!isMobile() && localStorage.getItem('sidebarCollapsed') === 'true') {
    sidebar && sidebar.classList.add('collapsed');
    mainArea && mainArea.classList.add('sidebar-collapsed');
  }

  // --- Active nav item ---
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item[data-href]').forEach(item => {
    if (currentPath.startsWith(item.dataset.href)) {
      item.classList.add('active');
    }
  });

  // --- Notification Dropdown ---
  const notifBtn = document.getElementById('notifBtn');
  const notifDropdown = document.getElementById('notifDropdown');

  if (notifBtn && notifDropdown) {
    notifBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      notifDropdown.classList.toggle('hidden');
    });
    document.addEventListener('click', function () {
      notifDropdown && notifDropdown.classList.add('hidden');
    });
  }

  // --- Auto-dismiss Toasts ---
  document.querySelectorAll('.toast').forEach(toast => {
    setTimeout(() => { toast.style.animation = 'slideIn 0.3s ease reverse'; setTimeout(() => toast.remove(), 300); }, 4000);
  });

  // --- Global search Ctrl+K ---
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const searchInput = document.querySelector('.topbar-search input');
      if (searchInput) searchInput.focus();
    }
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      const primaryForm = document.querySelector('form.primary-form');
      if (primaryForm) primaryForm.requestSubmit();
    }
  });

  // --- Unsaved changes warning ---
  let formChanged = false;
  document.querySelectorAll('form.primary-form').forEach(form => {
    form.querySelectorAll('input, select, textarea').forEach(el => {
      el.addEventListener('change', () => { formChanged = true; });
    });
    form.addEventListener('submit', () => { formChanged = false; });
  });

  window.addEventListener('beforeunload', function (e) {
    if (formChanged) {
      e.preventDefault();
      e.returnValue = 'You have unsaved changes.';
    }
  });

  // --- Table row click (open detail) ---
  document.querySelectorAll('.table-row-link').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function () {
      const href = this.dataset.href;
      if (href) window.location.href = href;
    });
  });

  // --- Confirm before destructive actions ---
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', function (e) {
      if (!window.confirm(this.dataset.confirm || 'Are you sure?')) {
        e.preventDefault();
      }
    });
  });

  // --- Invoice Item Management ---
  initBillingPage();
  initPaymentCalculator();
});

// =====================================================
// Billing page — dynamic item rows
// =====================================================
function initBillingPage() {
  const addItemBtn = document.getElementById('addItemBtn');
  const itemsTableBody = document.getElementById('invoiceItemsBody');

  if (!addItemBtn || !itemsTableBody) return;

  let itemCount = itemsTableBody.querySelectorAll('.item-row').length;

  addItemBtn.addEventListener('click', function () {
    itemCount++;
    const row = document.createElement('tr');
    row.className = 'item-row';
    row.innerHTML = `
      <td>${itemCount}</td>
      <td><input class="item-row-input item-product" type="text" placeholder="Search product..." autocomplete="off" data-index="${itemCount}"></td>
      <td><input class="item-row-input item-qty text-right" type="number" value="1" min="1" data-index="${itemCount}"></td>
      <td><input class="item-row-input item-rate text-right" type="number" step="0.01" placeholder="0.00" data-index="${itemCount}"></td>
      <td><input class="item-row-input item-tax text-right" type="number" value="0" step="0.01" data-index="${itemCount}"></td>
      <td class="item-amount text-right text-bold">₹0.00</td>
      <td>
        <button type="button" class="btn btn-ghost btn-icon btn-sm remove-item-btn" title="Remove">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </td>
    `;
    itemsTableBody.appendChild(row);
    attachItemRowEvents(row);
    row.querySelector('.item-product').focus();
  });

  // Attach to existing rows
  itemsTableBody.querySelectorAll('.item-row').forEach(row => attachItemRowEvents(row));
}

function attachItemRowEvents(row) {
  const qtyInput = row.querySelector('.item-qty');
  const rateInput = row.querySelector('.item-rate');
  const taxInput = row.querySelector('.item-tax');
  const amountCell = row.querySelector('.item-amount');
  const removeBtn = row.querySelector('.remove-item-btn');

  function recalcRow() {
    const qty = parseFloat(qtyInput?.value) || 0;
    const rate = parseFloat(rateInput?.value) || 0;
    const tax = parseFloat(taxInput?.value) || 0;
    const subtotal = qty * rate;
    const taxAmt = subtotal * (tax / 100);
    const total = subtotal + taxAmt;
    if (amountCell) amountCell.textContent = '₹' + total.toFixed(2);
    updateBillSummary();
  }

  [qtyInput, rateInput, taxInput].forEach(input => {
    if (input) input.addEventListener('input', recalcRow);
  });

  if (removeBtn) {
    removeBtn.addEventListener('click', function () {
      row.remove();
      updateBillSummary();
    });
  }
}

function updateBillSummary() {
  let subtotal = 0;
  document.querySelectorAll('.item-qty').forEach((qtyEl, i) => {
    const row = qtyEl.closest('tr');
    if (!row) return;
    const qty = parseFloat(qtyEl.value) || 0;
    const rate = parseFloat(row.querySelector('.item-rate')?.value) || 0;
    subtotal += qty * rate;
  });

  const discountEl = document.getElementById('discountInput');
  const discount = parseFloat(discountEl?.value) || 0;

  let taxTotal = 0;
  document.querySelectorAll('.item-qty').forEach((qtyEl) => {
    const row = qtyEl.closest('tr');
    if (!row) return;
    const qty = parseFloat(qtyEl.value) || 0;
    const rate = parseFloat(row.querySelector('.item-rate')?.value) || 0;
    const tax = parseFloat(row.querySelector('.item-tax')?.value) || 0;
    taxTotal += (qty * rate) * (tax / 100);
  });

  const grandTotal = subtotal - discount + taxTotal;
  const paidEl = document.getElementById('paidAmountInput');
  const paid = parseFloat(paidEl?.value) || 0;
  const due = grandTotal - paid;

  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = '₹' + val.toFixed(2); };
  set('summarySubtotal', subtotal);
  set('summaryTax', taxTotal);
  set('summaryTotal', grandTotal);
  set('summaryPaid', paid);
  set('summaryDue', due);

  const hiddenTotal = document.getElementById('grandTotalHidden');
  if (hiddenTotal) hiddenTotal.value = grandTotal.toFixed(2);

  const dueDisplay = document.getElementById('summaryDue');
  if (dueDisplay) {
    dueDisplay.className = due > 0 ? 'text-danger text-bold' : 'text-success text-bold';
  }
}

// =====================================================
// Payment Calculator
// =====================================================
function initPaymentCalculator() {
  const amountInput = document.getElementById('paymentAmountInput');
  const outstandingEl = document.getElementById('outstandingAmount');
  const newOutstandingEl = document.getElementById('newOutstandingDisplay');
  const errorEl = document.getElementById('paymentAmountError');

  if (!amountInput || !outstandingEl) return;

  amountInput.addEventListener('input', function () {
    const outstanding = parseFloat(outstandingEl.dataset.amount) || 0;
    const entered = parseFloat(this.value) || 0;
    const remaining = outstanding - entered;

    if (newOutstandingEl) newOutstandingEl.textContent = '₹' + Math.max(0, remaining).toFixed(2);

    if (entered > outstanding) {
      this.classList.add('error');
      if (errorEl) errorEl.textContent = 'Payment cannot exceed the outstanding amount of ₹' + outstanding.toFixed(2);
    } else {
      this.classList.remove('error');
      if (errorEl) errorEl.textContent = '';
    }
  });

  if (document.getElementById('discountInput')) {
    document.getElementById('discountInput').addEventListener('input', updateBillSummary);
  }
  if (document.getElementById('paidAmountInput')) {
    document.getElementById('paidAmountInput').addEventListener('input', updateBillSummary);
  }
}

// =====================================================
// Toast helper (call from Django messages or manually)
// =====================================================
function showToast(message, type = 'success') {
  const container = document.querySelector('.toast-container') || (() => {
    const c = document.createElement('div');
    c.className = 'toast-container';
    document.body.appendChild(c);
    return c;
  })();

  const icons = {
    success: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    error: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    warning: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/></svg>',
  };

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `${icons[type] || ''} <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => { toast.style.animation = 'slideIn 0.3s ease reverse'; setTimeout(() => toast.remove(), 300); }, 4000);
}
