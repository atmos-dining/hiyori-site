(() => {
  const siteUrl = window.HiyoriSite.url;
  const lightMotion = window.HiyoriSite.lightMotion;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const drawer = document.querySelector('.menu-drawer');
  const toggles = document.querySelectorAll('[data-menu-toggle]');
  let previousFocus;
  function setMenu(open) {
    if (!drawer) return;
    if (open) previousFocus = document.activeElement;
    drawer.hidden = !open;
    document.querySelectorAll('main, .site-header, .floating-menu, .access-section, .footer, .mobile-visit').forEach(el => { el.inert = open; });
    document.body.classList.toggle('menu-open', open);
    toggles.forEach(button => button.setAttribute('aria-expanded', String(open)));
    if (open) drawer.querySelector('button, a')?.focus();
    else previousFocus?.focus();
  }
  toggles.forEach(button => button.addEventListener('click', () => setMenu(drawer.hidden)));
  drawer?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', event => {
    if (!drawer || drawer.hidden) return;
    if (event.key === 'Escape') setMenu(false);
    if (event.key !== 'Tab') return;
    const focusable = [...drawer.querySelectorAll('a[href], button:not([disabled])')];
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  // Only update navigation when crossing the threshold. The curtain is CSS-driven.
  let scrolled;
  function setScrolled(next) {
    if (scrolled === next) return;
    scrolled = next;
    document.body.classList.toggle('scrolled', next);
  }
  const sentinel = document.querySelector('.scroll-sentinel');
  if (sentinel && 'IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      const entry = entries[entries.length - 1];
      setScrolled(!entry.isIntersecting && entry.boundingClientRect.bottom <= 0);
    }).observe(sentinel);
  } else {
    const updateNavigation = () => setScrolled(window.scrollY > 170);
    window.addEventListener('scroll', updateNavigation, { passive: true });
    updateNavigation();
  }
  if ('IntersectionObserver' in window && !reduceMotion.matches && !lightMotion) {
    document.body.classList.add('motion-ready');
    const reveals = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('visible'); reveals.unobserve(entry.target); }
    }), { threshold: .08 });
    document.querySelectorAll('.reveal').forEach(el => reveals.observe(el));
  }
  // A rejected autoplay or missing video always leaves its photograph visible.
  document.querySelectorAll('video[data-ambient-video]').forEach(video => {
    const button = video.parentElement.querySelector('[data-video-pause]');
    let manualPause = false;
    let inView = !('IntersectionObserver' in window);
    const canAnimate = () => !lightMotion && !reduceMotion.matches && !navigator.connection?.saveData;
    const startPlayback = () => {
      video.play().then(() => { video.classList.add('is-playing'); if (button) button.hidden = false; }).catch(() => {});
    };
    const play = () => {
      if (!canAnimate() || manualPause || document.hidden || !inView) return;
      startPlayback();
    };
    const syncButton = () => { if (button) { button.textContent = video.paused ? '▶' : 'Ⅱ'; button.setAttribute('aria-label', video.paused ? '動画を再生' : '動画を一時停止'); } };
    if (lightMotion && button) { button.hidden = false; syncButton(); }
    video.addEventListener('play', syncButton);
    video.addEventListener('pause', syncButton);
    video.addEventListener('error', () => { video.classList.remove('is-playing'); if (button) button.hidden = true; });
    button?.addEventListener('click', () => { manualPause = !video.paused; if (manualPause) video.pause(); else startPlayback(); });
    if ('IntersectionObserver' in window) {
      // Fetch once shortly before arrival; playback still waits until the video is visible.
      const prepare = new IntersectionObserver(entries => {
        if (!entries.some(entry => entry.isIntersecting) || !canAnimate()) return;
        video.preload = 'auto';
        video.load();
        play();
        prepare.disconnect();
      }, { rootMargin: '700px 0px' });
      prepare.observe(video);
      new IntersectionObserver(entries => {
        const entry = entries[entries.length - 1];
        inView = entry.isIntersecting && entry.intersectionRatio >= .12;
        if (inView) play();
        else video.pause();
      }, { threshold: [0, .12] }).observe(video);
    } else play();
    document.addEventListener('visibilitychange', () => { if (document.hidden) video.pause(); else play(); });
    reduceMotion.addEventListener('change', () => {
      if (reduceMotion.matches) {
        video.pause();
        video.classList.remove('is-playing');
        if (button) button.hidden = !lightMotion;
      } else play();
      if (lightMotion) syncButton();
    });
  });
  const roomData = {
    counter: { image:'counter', alt:'調理風景を眺める、ひよりの木のカウンター席', en:'AT THE COUNTER', title:'手仕事が見える、特等席。', text:'料理が仕上がる音や香りも、ごちそうのひとつ。オープンキッチンを目の前に、思い思いの一杯を。' },
    table: { image:'room', alt:'木のテーブルと柔らかな照明のテーブル席', en:'AROUND THE TABLE', title:'顔を合わせて、ゆっくりと。', text:'温かな照明と、木の手触り。ふたりでも、気の合う仲間とでも。お皿を囲んで過ごす、いつもの夜に。' },
    tatami: { image:'tatami', alt:'木の間仕切りに囲まれたひよりのお座敷', en:'A LITTLE MORE RELAXED', title:'靴をぬいで、ひと息。', text:'表情のある木の間仕切りと、落ち着いた畳の席。ゆっくり話したくなる夜にも、どうぞ。' }
  };
  const roomTabs = [...document.querySelectorAll('[data-room]')];
  function selectRoom(button, focus = false) {
    const data = roomData[button.dataset.room];
    roomTabs.forEach(tab => { const active = tab === button; tab.setAttribute('aria-selected',String(active)); tab.tabIndex = active ? 0 : -1; });
    const img = document.getElementById('room-image');
    if (img) { img.src = siteUrl(`/images/${data.image}-900.webp`); img.srcset = `${siteUrl(`/images/${data.image}-900.webp`)} 900w, ${siteUrl(`/images/${data.image}-1800.webp`)} 1800w`; img.alt = data.alt; }
    document.getElementById('room-en').textContent = data.en;
    document.getElementById('room-title').textContent = data.title;
    document.getElementById('room-text').textContent = data.text;
    document.getElementById('room-panel')?.setAttribute('aria-labelledby', button.id);
    if (focus) button.focus();
  }
  roomTabs.forEach((button,index) => {
    button.addEventListener('click', () => selectRoom(button));
    button.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % roomTabs.length;
      if (event.key === 'ArrowLeft') next = (index + roomTabs.length - 1) % roomTabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = roomTabs.length - 1;
      if (next !== undefined) { event.preventDefault(); selectRoom(roomTabs[next], true); }
    });
  });
  // Install listeners now; gtag may load asynchronously later.
  document.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link || typeof window.gtag !== 'function') return;
    const href = link.getAttribute('href') || '';
    if (href.startsWith('tel:')) window.gtag('event','phone_click',{event_category:'contact',event_label:href.slice(4),page_location:location.href});
    if (link.dataset.reservation !== undefined) window.gtag('event','reservation_click',{event_category:'conversion',event_label:link.textContent.trim().slice(0,50),page_location:location.href});
    if (link.dataset.map !== undefined) window.gtag('event','map_click',{event_category:'contact',page_location:location.href});
  });
})();
