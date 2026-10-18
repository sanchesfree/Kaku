document.querySelectorAll('.screenshot-gallery').forEach(gallery => {
  const tabs = [...gallery.querySelectorAll('[role="tab"]')];
  const panels = [...gallery.querySelectorAll('[role="tabpanel"]')];
  const mobile = window.matchMedia('(max-width: 560px)');

  function select(tab, focus = false) {
    tabs.forEach(item => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    panels.forEach(panel => {
      panel.hidden = panel.id !== tab.getAttribute('aria-controls');
    });
    if (focus) tab.focus();
  }

  function fitScreen() {
    const wide = tabs.find(tab => tab.hasAttribute('data-wide'));
    if (!wide) return;
    wide.hidden = mobile.matches;
    if (wide.hidden && wide.getAttribute('aria-selected') === 'true') {
      select(tabs.find(tab => !tab.hidden));
    }
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
      if (next) {
        event.preventDefault();
        select(next, true);
      }
    });
  });
  fitScreen();
  mobile.addEventListener('change', fitScreen);
  gallery.querySelector('[role="tablist"]').hidden = false;
});
