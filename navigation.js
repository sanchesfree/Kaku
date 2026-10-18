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

// Google Analytics counts visits in consent mode with storage denied, so it
// writes no cookies.
window.dataLayer = window.dataLayer || [];
window.gtag = function () { window.dataLayer.push(arguments); };
gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
gtag('js', new Date());
gtag('config', 'G-V8NF2P2W71');
const analytics = document.createElement('script');
analytics.async = true;
analytics.src = 'https://www.googletagmanager.com/gtag/js?id=G-V8NF2P2W71';
document.head.appendChild(analytics);
