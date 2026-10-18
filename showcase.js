document.querySelectorAll('.screenshot-gallery').forEach(gallery => {
  const tabs = [...gallery.querySelectorAll('[role="tab"]')];
  const panels = [...gallery.querySelectorAll('[role="tabpanel"]')];
  const frame = gallery.querySelector('.showcase-frame');
  const tablist = gallery.querySelector('[role="tablist"]');
  const caption = gallery.querySelector('.showcase-caption');
  panels.forEach(panel => {
    const link = panel.querySelector('a');
    const img = link.querySelector('img');
    const syncImageLink = () => { link.href = img.currentSrc || img.src; };
    img.addEventListener('load', syncImageLink);
    if (img.complete) syncImageLink();
  });
  let request = 0;
  let gesture;
  let swiped = false;

  async function select(tab, focus = false) {
    const currentRequest = ++request;
    const target = panels.find(panel => panel.id === tab.getAttribute('aria-controls'));
    const img = target.querySelector('img');
    if (focus) tab.focus({ preventScroll: true });
    frame.setAttribute('aria-busy', 'true');
    img.loading = 'eager';
    // Keep the current frame on screen while a cold image loads.
    try { await img.decode(); } catch (_) { /* The full-size link remains available. */ }
    if (currentRequest !== request) return;
    frame.removeAttribute('aria-busy');
    if (tab.hidden || !img.naturalWidth) return;
    tabs.forEach(item => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    panels.forEach(panel => { panel.hidden = panel !== target; });
    caption.textContent = tab.dataset.caption;
    const bounds = tab.getBoundingClientRect();
    const visible = tablist.getBoundingClientRect();
    if (bounds.left < visible.left) tablist.scrollLeft += bounds.left - visible.left;
    if (bounds.right > visible.right) tablist.scrollLeft += bounds.right - visible.right;
  }

  tabs.forEach(tab => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', event => {
      const visible = tabs.filter(item => !item.hidden);
      const index = visible.indexOf(tab);
      let next;
      if (event.key === 'ArrowRight') next = visible[(index + 1) % visible.length];
      if (event.key === 'ArrowLeft') next = visible[(index - 1 + visible.length) % visible.length];
      if (event.key === 'Home') next = visible[0];
      if (event.key === 'End') next = visible[visible.length - 1];
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
    const visible = tabs.filter(tab => !tab.hidden);
    const index = visible.findIndex(tab => tab.getAttribute('aria-selected') === 'true');
    select(visible[(index + (x < 0 ? 1 : -1) + visible.length) % visible.length]);
    swiped = true;
  });
  frame.addEventListener('click', event => {
    if (swiped) { event.preventDefault(); swiped = false; }
  }, true);
  tablist.hidden = false;
});
