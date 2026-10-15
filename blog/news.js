(async () => {
  const home = document.getElementById('home-news');
  const list = document.getElementById('post-list');
  if (!home && !list) return;
  const siteUrl = path => typeof window.HiyoriSite?.url === 'function' ? window.HiyoriSite.url(path) : path;

  function element(tag, text, className) {
    const el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
  }

  function articleLink(post, compact) {
    const link = element('a', undefined, compact ? 'news-row' : undefined);
    link.href = siteUrl(`/blog/posts/post.html?slug=${encodeURIComponent(post.slug)}`);
    const date = typeof post.date === 'string' ? post.date : '';
    if (date) {
      const time = element('time', compact ? date.replaceAll('-', '.') : date);
      time.dateTime = date;
      link.append(time);
    }
    link.append(element(compact ? 'span' : 'h2', post.title));
    if (compact) {
      const arrow = element('span', '↗', 'news-arrow');
      arrow.setAttribute('aria-hidden', 'true');
      link.append(arrow);
    } else if (typeof post.excerpt === 'string' && post.excerpt) {
      link.append(element('p', post.excerpt));
    }
    return link;
  }

  function content(posts, compact) {
    const fragment = document.createDocumentFragment();
    if (!posts.length) {
      fragment.append(element('p', 'ただいま、お知らせはありません。', 'news-empty'));
    } else {
      (compact ? posts.slice(0, 1) : posts).forEach(post => fragment.append(articleLink(post, compact)));
    }
    return fragment;
  }

  try {
    const response = await fetch(siteUrl('/blog/posts.json'), { cache: 'no-store' });
    if (!response.ok) return;
    const data = await response.json();
    if (!Array.isArray(data.posts) || !data.posts.every(post =>
      post && typeof post.slug === 'string' && post.slug.trim() &&
      typeof post.title === 'string' && post.title.trim()
    )) return;
    // Keep CMS order: add_to_top places the newest announcement first.
    const homeContent = home ? content(data.posts, true) : null;
    const listContent = list ? content(data.posts, false) : null;
    if (home) home.replaceChildren(homeContent);
    if (list) list.replaceChildren(listContent);
  } catch {
    // The generated HTML remains readable while the JSON is unavailable.
  }
})();
