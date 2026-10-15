(async () => {
  const root = document.getElementById('post-content');
  if (!root) return;
  const siteUrl = path => typeof window.HiyoriSite?.url === 'function' ? window.HiyoriSite.url(path) : path;
  const slug = new URLSearchParams(location.search).get('slug') || '';
  const validSlug = /^[a-z0-9][a-z0-9_-]{0,199}$/i.test(slug);
  const canonical = document.getElementById('canonical-link');
  let articleUrl = null;
  if (canonical && validSlug) {
    try {
      const configured = canonical.getAttribute('href') || '';
      if (/^https?:\/\//i.test(configured)) {
        const url = new URL(configured);
        url.search = '';
        url.hash = '';
        url.searchParams.set('slug', slug);
        canonical.href = url.href;
        document.getElementById('og-url')?.setAttribute('content', url.href);
        articleUrl = url;
      }
    } catch {
      // Preview pages without a configured public origin do not emit public URLs.
    }
  }
  const text = value => typeof value === 'string' ? value : '';
  function element(tag, value, className) {
    const el = document.createElement(tag);
    if (value !== undefined) el.textContent = text(value);
    if (className) el.className = className;
    return el;
  }
  function localImagePath(value) {
    if (typeof value !== 'string') return null;
    const imagesBase = siteUrl('/images/');
    const localValue = value.startsWith(imagesBase) ? '/images/' + value.slice(imagesBase.length) : value;
    const parts = localValue.replace(/^\//, '').split('/');
    if (parts.length < 2 || parts[0] !== 'images') return null;
    try {
      const decoded = parts.map(part => decodeURIComponent(part));
      if (decoded.some(part => !part || part === '.' || part === '..' || /[\\/\u0000-\u001f\u007f]/.test(part))) return null;
      return siteUrl('/' + decoded.map(part => encodeURIComponent(part)).join('/'));
    } catch {
      return null;
    }
  }
  const imagePaths = new Set();
  function image(value, alt, title, eager = false) {
    const path = localImagePath(value);
    if (!path) return null;
    const img = element('img');
    img.setAttribute('src', path);
    img.setAttribute('alt', text(alt));
    if (text(title)) img.setAttribute('title', title);
    img.setAttribute('loading', eager ? 'eager' : 'lazy');
    img.setAttribute('decoding', 'async');
    if (eager) img.setAttribute('fetchpriority', 'high');
    imagePaths.add(path);
    return img;
  }
  function photoFigure(img, className, caption) {
    const figure = element('figure', undefined, className);
    figure.append(img);
    if (text(caption)) figure.append(element('figcaption', caption));
    return figure;
  }
  function markdownBody(source) {
    const body = element('div', undefined, 'article-body');
    if (!window.marked) {
      source.split(/\n\s*\n/).forEach(paragraph => body.append(element('p', paragraph)));
      return body;
    }
    const template = document.createElement('template');
    template.innerHTML = window.marked.parse(source);
    const allowed = new Set(['P', 'H2', 'H3', 'H4', 'UL', 'OL', 'LI', 'STRONG', 'EM', 'DEL', 'BR', 'HR', 'BLOCKQUOTE', 'A', 'PRE', 'CODE', 'TABLE', 'THEAD', 'TBODY', 'TR', 'TH', 'TD']);
    function sanitize(node) {
      for (const child of [...node.childNodes]) {
        if (child.nodeType === 3) continue;
        if (child.nodeType !== 1) { child.remove(); continue; }
        if (child.tagName === 'IMG') {
          const img = image(child.getAttribute('src'), child.getAttribute('alt'), child.getAttribute('title'));
          if (img) child.replaceWith(img);
          else child.remove();
          continue;
        }
        if (!allowed.has(child.tagName)) {
          child.replaceWith(document.createTextNode(child.textContent || ''));
          continue;
        }
        const href = child.tagName === 'A' ? child.getAttribute('href') : null;
        for (const attr of [...child.attributes]) child.removeAttribute(attr.name);
        if (href && (/^https?:\/\//i.test(href) || /^\/(?![\/\\])/.test(href) || href.startsWith('#'))) child.setAttribute('href', siteUrl(href));
        sanitize(child);
      }
    }
    sanitize(template.content);
    // Markdown emits a paragraph around standalone images; give photos a captionable block.
    for (const paragraph of template.content.querySelectorAll('p')) {
      const meaningful = [...paragraph.childNodes].filter(node => node.nodeType !== 3 || node.textContent.trim());
      if (meaningful.length && meaningful.every(node => node.nodeType === 1 && node.tagName === 'IMG')) {
        paragraph.replaceWith(...meaningful.map(img => photoFigure(img, 'article-photo', img.getAttribute('title'))));
      }
    }
    body.append(template.content);
    return body;
  }
  try {
    if (!validSlug) {
      root.replaceChildren(element('h1', 'お便りが見つかりませんでした。'));
    } else {
      const response = await fetch(siteUrl('/blog/posts.json'), { cache: 'no-store' });
      if (!response.ok) throw new Error('load');
      const data = await response.json();
      if (!Array.isArray(data.posts)) throw new Error('invalid posts');
      const post = data.posts.find(item => item && item.slug === slug);
      if (!post || !text(post.title).trim()) {
        root.replaceChildren(element('h1', 'お便りが見つかりませんでした。'));
      } else {
        document.title = `${post.title}｜肴とお野菜 ひより`;
        document.querySelector('meta[name="description"]')?.setAttribute('content', text(post.excerpt));
        document.querySelector('meta[property="og:title"]')?.setAttribute('content', document.title);
        document.querySelector('meta[property="og:description"]')?.setAttribute('content', text(post.excerpt));
        document.querySelector('meta[property="og:type"]')?.setAttribute('content', 'article');

        const header = element('header', undefined, 'article-header');
        const meta = element('div', undefined, 'article-meta');
        if (text(post.date)) {
          const date = element('time', post.date);
          date.dateTime = post.date;
          meta.append(date);
        }
        if (Array.isArray(post.tags)) {
          const tags = element('ul', undefined, 'article-tags');
          post.tags.filter(tag => text(tag).trim()).forEach(tag => tags.append(element('li', tag)));
          if (tags.childNodes.length) meta.append(tags);
        }
        header.append(meta, element('h1', post.title));
        root.replaceChildren(header);
        const cover = image(post.image, text(post.imageAlt) || post.title, '', true);
        if (cover) root.append(photoFigure(cover, 'article-cover', post.imageCaption));
        root.append(markdownBody(text(post.body) || text(post.excerpt)));

        if (articleUrl) {
          const images = [...imagePaths].map(path => new URL(path, articleUrl.origin).href);
          if (images.length) {
            let ogImage = document.querySelector('meta[property="og:image"]');
            if (!ogImage) {
              ogImage = element('meta');
              ogImage.setAttribute('property', 'og:image');
              document.head.append(ogImage);
            }
            ogImage.setAttribute('content', images[0]);
          }
          const schema = {
            '@context': 'https://schema.org', '@type': 'BlogPosting',
            headline: post.title, description: text(post.excerpt),
            url: articleUrl.href, mainEntityOfPage: articleUrl.href,
            publisher: { '@type': 'Organization', name: '肴とお野菜 ひより' }
          };
          if (text(post.date)) schema.datePublished = post.date;
          if (images.length) schema.image = images;
          const structuredData = element('script');
          structuredData.id = 'article-structured-data';
          structuredData.type = 'application/ld+json';
          structuredData.textContent = JSON.stringify(schema);
          document.getElementById(structuredData.id)?.remove();
          document.head.append(structuredData);
        }
      }
    }
  } catch {
    root.replaceChildren(element('h1', 'お便りを表示できませんでした。'), element('p', '時間をおいて、もう一度お試しください。'));
  }
  const back = element('a', 'ひより便りの一覧へ →', 'article-back');
  back.href = siteUrl('/blog/');
  root.append(back);
})();
