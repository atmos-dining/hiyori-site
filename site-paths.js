(() => {
  const basePath = (document.querySelector('meta[name="site-base-path"]')?.getAttribute('content') || '').replace(/\/+$/, '');
  function url(path) {
    if (typeof path !== 'string' || !basePath || !path.startsWith('/') || path.startsWith('//')) return path;
    const pathname = path.split(/[?#]/, 1)[0];
    if (pathname === basePath || pathname.startsWith(`${basePath}/`)) return path;
    return basePath + path;
  }
  window.HiyoriSite = { url };
})();
