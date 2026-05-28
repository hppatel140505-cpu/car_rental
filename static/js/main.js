// DriveEase — Main JavaScript

document.addEventListener('DOMContentLoaded', function () {

  // =============================================
  // AUTO-DISMISS ALERT MESSAGES (4 seconds)
  // =============================================
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'all 0.4s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(30px)';
      setTimeout(function () { alert.remove(); }, 400);
    }, 4000);
  });

  // =============================================
  // ACTIVE NAV LINK HIGHLIGHTING
  // =============================================
  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar__links a').forEach(function (link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // =============================================
  // QUANTITY SPINNER VALIDATION
  // =============================================
  const qtyInput = document.getElementById('qty-input');
  if (qtyInput) {
    qtyInput.addEventListener('change', function () {
      const max = parseInt(this.getAttribute('max')) || 999;
      if (parseInt(this.value) < 1) this.value = 1;
      if (parseInt(this.value) > max) this.value = max;
    });
  }

  // =============================================
  // MY BOOKINGS PAGE — Tab Switcher
  // =============================================
  (function () {
    const cards = document.querySelectorAll('.booking-item-card');
    if (cards.length === 0) return;

    const tabs = document.querySelectorAll('.booking-tab');
    const activeCountBadge  = document.getElementById('badge-active-count');
    const historyCountBadge = document.getElementById('badge-history-count');
    const emptyActive       = document.getElementById('empty-active');
    const emptyHistory      = document.getElementById('empty-history');
    const grid              = document.getElementById('bookings-grid');

    // Count active vs history
    let activeCount = 0, historyCount = 0;
    cards.forEach(function (card) {
      card.dataset.isPast === 'true' ? historyCount++ : activeCount++;
    });
    if (activeCountBadge)  activeCountBadge.textContent  = activeCount;
    if (historyCountBadge) historyCountBadge.textContent = historyCount;

    function switchTab(targetTab) {
      tabs.forEach(function (tab) {
        tab.classList.toggle('active', tab.dataset.tab === targetTab);
      });

      let visibleCards = 0;
      cards.forEach(function (card) {
        const isPast = card.dataset.isPast === 'true';
        const show   = (targetTab === 'active') ? !isPast : isPast;
        card.style.display = show ? '' : 'none';
        if (show) {
          card.style.animation = 'fadeInUp 0.4s ease forwards';
          visibleCards++;
        }
      });

      if (visibleCards === 0) {
        if (grid)         grid.style.display         = 'none';
        if (emptyActive)  emptyActive.style.display  = (targetTab === 'active')  ? 'block' : 'none';
        if (emptyHistory) emptyHistory.style.display = (targetTab === 'history') ? 'block' : 'none';
      } else {
        if (grid)         grid.style.display         = '';
        if (emptyActive)  emptyActive.style.display  = 'none';
        if (emptyHistory) emptyHistory.style.display = 'none';
      }
    }

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () { switchTab(tab.dataset.tab); });
    });

    switchTab('active');
  })();

  // =============================================
  // OUR FLEET PAGE — Filter Chips + Search
  // =============================================
  (function () {
    const chips = document.querySelectorAll('.fleet-chip');
    if (chips.length === 0) return;

    const fleetCards  = document.querySelectorAll('.fleet-card-link');
    const noResults   = document.getElementById('no-results');
    const fleetSearch = document.getElementById('product-search');
    let activeCategory = 'all';

    function filterFleetCards() {
      const q = fleetSearch ? fleetSearch.value.trim().toLowerCase() : '';
      let visible = 0;
      fleetCards.forEach(function (card) {
        const cat  = card.dataset.category || '';
        const name = card.dataset.name     || '';
        const catMatch    = activeCategory === 'all' || cat === activeCategory;
        const searchMatch = q === '' || name.includes(q) || cat.toLowerCase().includes(q);
        const show = catMatch && searchMatch;
        card.style.display = show ? '' : 'none';
        if (show) {
          card.style.animation = 'fadeInUp 0.35s ease forwards';
          visible++;
        }
      });
      if (noResults) noResults.style.display = visible === 0 ? 'block' : 'none';
    }

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.forEach(function (c) { c.classList.remove('active'); });
        chip.classList.add('active');
        activeCategory = chip.dataset.category;
        filterFleetCards();
      });
    });

    if (fleetSearch) fleetSearch.addEventListener('input', filterFleetCards);
  })();

  // =============================================
  // CAR DETAIL PAGE — Booking Date Calculator
  // reads price from <span id="car-price-data" data-price="...">
  // =============================================
  (function () {
    const priceEl = document.getElementById('car-price-data');
    if (!priceEl) return;

    const pricePerDay = Number(priceEl.dataset.price);
    const pickupInput      = document.getElementById('id_pickup_date');
    const returnInput      = document.getElementById('id_return_date');
    const daysSpan         = document.getElementById('days-count');
    const estimatorBox     = document.getElementById('invoice-estimator');
    const invoiceDaysCount = document.getElementById('invoice-days-count');
    const invoiceBaseRent  = document.getElementById('invoice-base-rent');
    const invoiceGrandTotal = document.getElementById('invoice-grand-total');

    function calcDays() {
      const p = pickupInput ? pickupInput.value : '';
      const r = returnInput ? returnInput.value : '';
      if (p && r) {
        const diff = Math.round((new Date(r) - new Date(p)) / (1000 * 60 * 60 * 24));
        if (diff > 0) {
          if (daysSpan)         daysSpan.textContent         = diff + ' day' + (diff > 1 ? 's' : '');
          if (invoiceDaysCount) invoiceDaysCount.textContent = diff;
          const baseRent = pricePerDay * diff;
          if (invoiceBaseRent)   invoiceBaseRent.textContent   = '₹' + baseRent.toLocaleString('en-IN');
          if (invoiceGrandTotal) invoiceGrandTotal.textContent = '₹' + baseRent.toLocaleString('en-IN');
          if (estimatorBox)      estimatorBox.style.display    = 'block';
        } else {
          if (daysSpan)     daysSpan.textContent     = '—';
          if (estimatorBox) estimatorBox.style.display = 'none';
        }
      } else {
        if (estimatorBox) estimatorBox.style.display = 'none';
      }
    }

    if (pickupInput) pickupInput.addEventListener('change', calcDays);
    if (returnInput) returnInput.addEventListener('change', calcDays);
  })();

});
