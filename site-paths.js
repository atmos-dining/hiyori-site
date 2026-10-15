(() => {
  // LINE uses an embedded browser; keep motion conservative without changing content.
  const lightMotion = /\bLine\/\d/i.test(navigator.userAgent);
  if (lightMotion) document.documentElement.classList.add('light-motion');
  const basePath = (document.querySelector('meta[name="site-base-path"]')?.getAttribute('content') || '').replace(/\/+$/, '');
  function url(path) {
    if (typeof path !== 'string' || !basePath || !path.startsWith('/') || path.startsWith('//')) return path;
    const pathname = path.split(/[?#]/, 1)[0];
    if (pathname === basePath || pathname.startsWith(`${basePath}/`)) return path;
    return basePath + path;
  }
  window.HiyoriSite = { url, lightMotion };
})();
