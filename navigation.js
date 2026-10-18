document.querySelectorAll('.lang-switch').forEach(switcher => {
  const trigger = switcher.querySelector('summary');
  const links = [...switcher.querySelectorAll('a')];
  switcher.addEventListener('keydown', event => {
    if (event.key === 'Escape' && switcher.open) {
      event.preventDefault();
      switcher.open = false;
      trigger.focus();
    }
    if (event.target === trigger && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
      event.preventDefault();
      switcher.open = true;
      links[event.key === 'ArrowDown' ? 0 : links.length - 1].focus();
    }
  });
  document.addEventListener('click', event => {
    if (!switcher.contains(event.target)) switcher.open = false;
  });
  switcher.addEventListener('focusout', event => {
    if (!switcher.contains(event.relatedTarget)) switcher.open = false;
  });
});
