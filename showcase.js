document.querySelectorAll('[data-gallery]').forEach(gallery => {
  const tabs = [...gallery.querySelectorAll('[role="tab"]')];
  const panels = [...gallery.querySelectorAll('[role="tabpanel"]')];
  const frame = gallery.querySelector('.gallery-frame');
  const tablist = gallery.querySelector('[role="tablist"]');
  const title = gallery.querySelector('[data-gallery-title]');
  const line = gallery.querySelector('[data-gallery-line]');
  let request = 0;
  let fadeTimer;
  let gesture;
  let swiped = false;

  // Fetch the other captures once the page is idle, so a click swaps at once.
  const warm = () => panels.forEach(panel => {
    const img = panel.querySelector('img');
    img.loading = 'eager';
    img.decode().catch(() => {});
  });
  const idle = window.requestIdleCallback || (fn => setTimeout(fn, 600));
  if (document.readyState === 'complete') idle(warm);
  else window.addEventListener('load', () => idle(warm), { once: true });

  async function select(tab, focus = false) {
    const currentRequest = ++request;
    const target = panels.find(panel => panel.id === tab.getAttribute('aria-controls'));
    const current = panels.find(panel => panel.classList.contains('is-active'));
    const img = target.querySelector('img');
    if (focus) tab.focus({ preventScroll: true });
    tabs.forEach(item => {
      const selected = item === tab;
      item.classList.toggle('is-active', selected);
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    title.textContent = tab.dataset.title;
    line.textContent = tab.dataset.line;
    const bounds = tab.getBoundingClientRect();
    const visible = tablist.getBoundingClientRect();
    if (bounds.left < visible.left) tablist.scrollLeft += bounds.left - visible.left;
    if (bounds.right > visible.right) tablist.scrollLeft += bounds.right - visible.right;
    if (target === current) return;
    img.loading = 'eager';
    // Keep the current frame on screen while a cold image loads.
    if (!img.complete) { try { await img.decode(); } catch (_) { /* The full-size link remains available. */ } }
    if (currentRequest !== request) return;
    clearTimeout(fadeTimer);
    panels.forEach(panel => panel.classList.remove('was-active'));
    if (current) {
      current.classList.remove('is-active');
      current.classList.add('was-active');
      current.setAttribute('aria-hidden', 'true');
    }
    target.classList.add('is-active');
    target.removeAttribute('aria-hidden');
    fadeTimer = setTimeout(() => current && current.classList.remove('was-active'), 260);
  }

  tabs.forEach(tab => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', event => {
      const index = tabs.indexOf(tab);
      let next;
      if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
      if (event.key === 'ArrowLeft') next = tabs[(index - 1 + tabs.length) % tabs.length];
      if (event.key === 'Home') next = tabs[0];
      if (event.key === 'End') next = tabs[tabs.length - 1];
      if (next) { event.preventDefault(); select(next, true); }
    });
  });
  frame.addEventListener('pointerdown', event => {
    swiped = false;
    gesture = event.pointerType === 'touch' && event.isPrimary ? { x: event.clientX, y: event.clientY } : null;
  });
  frame.addEventListener('pointercancel', () => { gesture = null; });
  frame.addEventListener('pointerup', event => {
    if (!gesture) return;
    const x = event.clientX - gesture.x;
    const y = event.clientY - gesture.y;
    gesture = null;
    if (Math.abs(x) < 48 || Math.abs(x) < Math.abs(y) * 1.3) return;
    const index = tabs.findIndex(tab => tab.getAttribute('aria-selected') === 'true');
    select(tabs[(index + (x < 0 ? 1 : -1) + tabs.length) % tabs.length]);
    swiped = true;
  });
  // Like mole.fit: a click on the left half steps back, on the right half forward.
  frame.addEventListener('click', event => {
    if (swiped) { swiped = false; return; }
    const box = frame.getBoundingClientRect();
    const index = tabs.findIndex(tab => tab.getAttribute('aria-selected') === 'true');
    const step = event.clientX < box.left + box.width / 2 ? -1 : 1;
    select(tabs[(index + step + tabs.length) % tabs.length]);
  });
});
