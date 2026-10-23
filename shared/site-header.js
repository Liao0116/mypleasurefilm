(() => {
  const header = document.querySelector('.site-header');
  if (!header) return;
  const toggle = header.querySelector('.site-menu-toggle');
  const navigation = header.querySelector('.site-navigation');
  const desktop = window.matchMedia('(min-width: 1200px)');

  const setOpen = (open) => {
    header.toggleAttribute('data-menu-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? '關閉主選單' : '開啟主選單');
  };

  toggle.hidden = false;
  header.setAttribute('data-enhanced', '');
  toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) setOpen(false);
  });
  document.addEventListener('click', (event) => {
    if (!header.contains(event.target)) setOpen(false);
  });
  header.addEventListener('focusout', (event) => {
    if (!header.contains(event.relatedTarget)) setOpen(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      setOpen(false);
      toggle.focus();
    }
  });
  desktop.addEventListener('change', () => {
    const active = document.activeElement;
    setOpen(false);
    if (desktop.matches && active === toggle) navigation.querySelector('a').focus();
    if (!desktop.matches && navigation.contains(active)) toggle.focus();
  });
})();
