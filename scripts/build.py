#!/usr/bin/env python3
"""Generate static, crawlable pages using only Python's standard library."""
import hashlib, html, json, os, re
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / 'site-config.json').read_text())
menus = json.loads((ROOT / 'menu-data.json').read_text())
photos = json.loads((ROOT / 'photo-assets.json').read_text())
site_url = os.environ.get('SITE_URL', cfg.get('origin', '')).strip().rstrip('/')
base_path = urlsplit(site_url).path.rstrip('/')
indexable_env = os.environ.get('SITE_INDEXABLE')
indexable = indexable_env == 'true' if indexable_env is not None else cfg.get('indexable', bool(cfg.get('origin')))
esc = html.escape
map_url = esc(cfg['mapUrl'], quote=True)
links = [('/', 'ひよりについて'), ('/menu.html', 'お料理'), ('/drink.html', 'お飲み物'), ('/space.html', 'お席と空間'), ('/access.html', 'ご来店案内')]

def asset_url(name):
    """Reload changed shared assets even when an in-app browser keeps its cache."""
    version = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()[:12]
    return f'/{name}?v={version}'

def site_path(value):
    """Prefix site-root URLs once, preserving external URLs and query strings."""
    if not base_path or not value.startswith('/') or value.startswith('//'):
        return value
    pathname = re.split(r'[?#]', value, maxsplit=1)[0]
    if pathname == base_path or pathname.startswith(base_path + '/'):
        return value
    return base_path + value

def page_paths(markup):
    def replace_attr(match):
        value = match.group('value')
        if match.group('name').lower() == 'srcset':
            value = re.sub(r'(^|,\s*)(/(?!/)[^\s,]+)', lambda item: item.group(1) + site_path(item.group(2)), value)
        else:
            value = site_path(value)
        return match.group('name') + match.group('equals') + match.group('quote') + value + match.group('quote')
    return re.sub(r'''(?<![\w:-])(?P<name>href|src|poster|srcset)(?P<equals>\s*=\s*)(?P<quote>["'])(?P<value>.*?)(?P=quote)''', replace_attr, markup, flags=re.I | re.S)

def image(name, alt, cls='', eager=False, image_id=''):
    identity = f' id="{esc(image_id, quote=True)}"' if image_id else ''
    return f'<img{identity} class="{cls}" src="/images/{name}-900.webp" srcset="/images/{name}-900.webp 900w, /images/{name}-1800.webp 1800w" sizes="(max-width:700px) 100vw, 75vw" width="1800" height="1013" alt="{esc(alt)}" {"fetchpriority=high" if eager else "loading=lazy"} decoding="async">'

def photo(name, alt, sizes='(max-width:700px) 100vw, 50vw', image_id=''):
    """Use real source dimensions and responsive copies without enlarging originals."""
    data = photos[name]
    variants = data['variants']
    src = next(v['file'] for v in variants if v['width'] == 900)
    srcset = ', '.join(f'/images/{v["file"]} {v["width"]}w' for v in variants)
    identity = f' id="{esc(image_id, quote=True)}"' if image_id else ''
    return f'<img{identity} class="photo-{name}" src="/images/{src}" srcset="{srcset}" sizes="{sizes}" width="{data["width"]}" height="{data["height"]}" alt="{esc(alt, quote=True)}" loading="lazy" decoding="async">'

def photo_figure(name, alt, caption='', cls=''):
    label = f'<figcaption>{esc(caption)}</figcaption>' if caption else ''
    return f'<figure class="{cls}">{photo(name, alt)}{label}</figure>'

def reservation_link(cls=''):
    if not cfg['reservationUrl']:
        return ''
    return f'<a class="reservation-button {cls}" data-reservation href="{esc(cfg["reservationUrl"], quote=True)}" target="_blank" rel="noopener noreferrer"><span>お席を予約する</span><span aria-hidden="true">↗</span></a>'

def header():
    return f'''<span class="scroll-sentinel" aria-hidden="true"></span><a class="skip" href="#main">本文へ進む</a>
<header class="site-header"><a href="/" class="brand-small" aria-label="肴とお野菜 ひより トップ"><span class="seal" aria-hidden="true">日</span><span class="brand-word">ひより</span></a><div class="header-right"><a class="header-visit" href="/access.html">ご来店案内</a>{reservation_link('header-reservation')}<button class="menu-toggle" data-menu-toggle aria-label="メニューを開く" aria-expanded="false" aria-controls="site-menu"><span></span><span></span></button></div></header>
{reservation_link('floating-reservation')}
<button class="menu-toggle floating-menu" data-menu-toggle aria-label="メニューを開く" aria-expanded="false" aria-controls="site-menu"><span></span><span></span></button>
<div class="menu-drawer" id="site-menu" role="dialog" aria-modal="true" aria-label="サイトメニュー" hidden><button class="menu-toggle drawer-close" data-menu-toggle aria-label="メニューを閉じる" aria-expanded="true" aria-controls="site-menu"><span></span><span></span></button><div class="drawer-brand" aria-hidden="true">ひより</div><div><nav class="drawer-links" aria-label="メインナビゲーション">''' + ''.join(f'<a href="{u}"><small>0{i}</small>{t}</a>' for i,(u,t) in enumerate(links,1)) + f'''<a href="/blog/"><small>06</small>ひより便り</a></nav>{reservation_link('drawer-reservation')}<div class="drawer-bottom">肴とお野菜 ひより<br>福岡・天神南 / 渡辺通</div></div></div>'''

def details():
    rows = [('店名', cfg['name']), ('所在地', cfg['address'])]
    if cfg['hours']: rows.append(('営業時間', cfg['hours']))
    if cfg['closed']: rows.append(('定休日', cfg['closed']))
    out = '<dl class="access-details">' + ''.join(f'<div><dt>{k}</dt><dd>{esc(v)}</dd></div>' for k,v in rows)
    if cfg['telephone']:
        tel = re.sub(r'[^+0-9]', '', cfg['telephone'])
        out += f'<div><dt>お電話</dt><dd><a href="tel:{tel}">{esc(cfg["telephone"])}</a></dd></div>'
    return out + '</dl>'

def visit_links():
    return reservation_link('visit-reservation') + f'<a class="map-link" data-map href="{map_url}" target="_blank" rel="noopener noreferrer">Googleマップで場所を見る<span aria-hidden="true">↗</span></a>'

def footer(full=True):
    mobile_visit = f'<nav class="mobile-visit mobile-booking" aria-label="ご来店・ご予約"><a href="/access.html">ご来店案内</a>{reservation_link("mobile-reservation")}</nav>' if cfg['reservationUrl'] else '<a class="mobile-visit" href="/access.html"><span>天神南で、ひより。</span><span>ご来店案内&nbsp; ↗</span></a>'
    return (f'''<section class="access-section" id="access"><div class="wrap access-grid"><div><div class="section-number">ご来店案内</div><h2>今夜、ひよりで。</h2><p class="store-title">肴とお野菜 ひより</p><p>天神南、渡辺通。<br>暖簾の向こうで、お待ちしています。</p></div><div>{details()}{visit_links()}</div></div></section>''' if full else '') + '''<footer class="footer"><div class="wrap footer-inner"><nav class="footer-links" aria-label="フッターナビゲーション">''' + ''.join(f'<a href="{u}">{t}</a>' for u,t in links) + '''<a href="/blog/">ひより便り</a></nav><span>© HIYORI. ALL RIGHTS RESERVED.</span></div></footer>''' + mobile_visit

def head(title, description, path, extra=''):
    canonical = f'<link rel="canonical" id="canonical-link" href="{esc(site_url+path, quote=True)}"><meta property="og:url" id="og-url" content="{esc(site_url+path, quote=True)}">' if site_url else ''
    robots = '' if indexable else '<meta name="robots" content="noindex,nofollow">'
    og_img = f'<meta property="og:image" content="{esc(site_url, quote=True)}/images/room-1800.webp">' if site_url else ''
    analytics = ''
    if re.fullmatch(r'G-[A-Z0-9]+',cfg['ga4Id']):
        gid = cfg['ga4Id']
        analytics = f'<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{gid}");</script>'
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>{esc(title)}</title><meta name="description" content="{esc(description, quote=True)}"><meta name="theme-color" content="#f2efe5"><meta name="site-base-path" content="{esc(base_path, quote=True)}">{robots}{canonical}<meta property="og:type" content="website"><meta property="og:locale" content="ja_JP"><meta property="og:site_name" content="肴とお野菜 ひより"><meta property="og:title" content="{esc(title, quote=True)}"><meta property="og:description" content="{esc(description, quote=True)}">{og_img}<link rel="icon" type="image/svg+xml" href="/favicon.svg"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500&amp;family=Shippori+Mincho:wght@400;500;600;700;800&amp;display=swap"><link rel="stylesheet" href="{asset_url('style.css')}"><script src="{asset_url('site-paths.js')}"></script><script src="{asset_url('common.js')}" defer></script>{extra}{analytics}</head>'''

def write_page(path, title, desc, body, home=False, full_footer=True, extra=''):
    target = ROOT / (path.lstrip('/') or 'index.html')
    if path.endswith('/') and path != '/': target = target / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    # Homepage header lives over the curtain; all body copy is in the initial HTML.
    target.write_text(page_paths(head(title,desc,path,extra) + f'<body class="{"homepage" if home else "subpage"}">' + header() + '<main id="main">' + body + '</main>' + footer(full_footer) + '</body></html>'))


def optional_clip(key, alt):
    source = cfg.get(key, '')
    video = ROOT / source.lstrip('/')
    poster = video.with_suffix('.jpg')
    if not source or not video.is_file() or not poster.is_file(): return ''
    poster_url = '/' + str(poster.relative_to(ROOT))
    return f'<figure class="taste-media"><img src="{esc(poster_url,quote=True)}" alt="{esc(alt,quote=True)}" width="1600" height="1000" loading="lazy"><video data-ambient-video muted loop playsinline preload="none" poster="{esc(poster_url,quote=True)}" aria-hidden="true"><source src="{esc(source,quote=True)}" type="video/mp4"></video><button class="video-pause" data-video-pause aria-label="動画を一時停止" hidden>Ⅱ</button></figure>'

hero_video = ''
if cfg['heroVideo'] and (ROOT / cfg['heroVideo'].lstrip('/')).is_file():
    hero_poster = cfg['heroVideo'].rsplit('.',1)[0]+'.jpg'
    if not (ROOT/hero_poster.lstrip('/')).is_file(): hero_poster='/images/room-1800.webp'
    hero_video = f'<video class="hero-video" data-ambient-video muted loop playsinline preload="none" poster="{esc(hero_poster,quote=True)}" aria-hidden="true"><source src="{esc(cfg["heroVideo"],quote=True)}" type="video/mp4"></video><button class="hero-pause" data-video-pause aria-label="動画を一時停止" hidden>Ⅱ</button>'

posts_path=ROOT/'blog/posts.json'
if not posts_path.exists():
    posts_path.parent.mkdir(parents=True,exist_ok=True)
    posts_path.write_text(json.dumps({'posts':[{'slug':'opening','title':'天神南に、ひよりの暖簾を。','date':'2026-10-14','excerpt':'肴とお野菜 ひよりが、天神南・渡辺通にオープンしました。','image':'/images/room-1800.webp','tags':['お知らせ'],'body':'肴とお野菜 ひよりが、天神南・渡辺通にオープンしました。\n\nお席で仕上げるサワラの藁焼き。ひと工夫を加えたお野菜のひと皿。締めくくりには、炊き立ての土鍋ご飯を。\n\nカウンター、テーブル、お座敷。それぞれのお席で、くつろぎの時間をお過ごしください。\n\nみなさまのお越しを、お待ちしています。'}]},ensure_ascii=False,indent=2))
posts=json.loads(posts_path.read_text())['posts']

home_news = ''.join(f'<a class="news-row" href="/blog/posts/post.html?slug={quote(p["slug"])}"><time datetime="{esc(p["date"])}">{esc(p["date"].replace("-","."))}</time><span>{esc(p["title"])}</span><span class="news-arrow" aria-hidden="true">↗</span></a>' for p in posts[:1]) or '<p>新しいお便りを、どうぞお楽しみに。</p>'

home = f'''<section class="hero" aria-label="肴とお野菜 ひよりへようこそ">
{image('room','木の温かさと柔らかい灯りが迎える、ひよりの店内','hero-image',True)}{hero_video}
<div class="noren"><div class="noren-panels" aria-hidden="true"><div class="cloth"></div><div class="cloth"></div><div class="cloth"></div></div><div class="hero-brand"><span class="brand-stamp" aria-hidden="true">天神南</span><h1>ひより</h1><span class="brand-category">肴とお野菜</span></div><p class="hero-side">いい肴と、お野菜と。<br>今日も、いい日より。</p><nav class="hero-nav" aria-label="入口のご案内"><a href="/menu.html">お料理</a><a href="/drink.html">お飲み物</a><a href="/space.html">お席と空間</a><a href="/access.html">ご来店案内</a></nav>{reservation_link("hero-reservation")}</div>
<p class="hero-catch">いい日も、<br>なんでもない日も。</p><div class="hero-bottom"><p class="eyebrow">SAKANA TO OYASAI<br>FUKUOKA, TENJINMINAMI</p><p class="small">肴とお野菜 ひより</p></div><a class="scroll-invitation" href="#hiyori"><span>暖簾をくぐる</span><span class="scroll-line" aria-hidden="true"></span></a></section>
<section class="intro" id="hiyori"><div class="wrap"><div class="intro-top"><div class="reveal"><div class="section-number">ひよりについて</div><h2 class="heading">旬をつまんで、<br>ほっと、ひと息。</h2></div><div class="intro-copy reveal"><p>一日の終わりに、ひと皿と一杯。<br>気の合う人と、話のつづき。</p><p>香ばしい肴に、ひと工夫のお野菜。<br>締めくくりには、炊き立ての土鍋ご飯。<br>食べるほどに、気持ちまでほぐれていく。</p><p>天神南の「肴とお野菜 ひより」。<br>なんでもない日が、ちょっといい日になる。<br>そんな時間を、ご一緒に。</p></div></div><figure class="intro-photo reveal">{photo('about-carpaccio','ガラスの器に盛り付けた鮮魚と彩り野菜のひと皿')}<figcaption>THE EVERYDAY, A LITTLE MORE SPECIAL.</figcaption><p class="intro-note">気取らずに。<br>でも、ひと皿は丁寧に。</p></figure></div><span class="intro-mark" aria-hidden="true">日和</span></section>
<section class="food-world" id="food"><div class="wrap"><div class="food-heading reveal"><div><div class="section-number">ひよりのお料理</div><h2 class="heading">火の香り。旬の彩り。<br>炊きたての、幸せ。</h2></div><p class="vertical">肴も、お野菜も。<br>今日の食べたい、を少しずつ。</p></div><figure class="plating-scene"><img src="/videos/plating-poster.jpg" alt="ひよりの厨房で、ひと皿ずつ料理を盛り付ける手元" width="1600" height="900" loading="lazy"><video data-ambient-video muted loop playsinline preload="none" poster="/videos/plating-poster.jpg" aria-hidden="true"><source src="/videos/plating.mp4" type="video/mp4"></video><figcaption class="scene-copy">ひと皿ずつ、<br>手をかけて。</figcaption><button class="video-pause" data-video-pause aria-label="動画を一時停止" hidden>Ⅱ</button></figure>
<div class="three-tastes"><article class="taste reveal">{optional_clip("fireVideo","お席で仕上げるサワラの藁焼き") or photo_figure("food-sawara","藁と柑橘を添えたサワラの藁焼き",cls="taste-media")}<span class="taste-num">01 / SAKANA</span><h3>香りまで、ごちそう。</h3><p>名物は、お席で仕上げるサワラの藁焼き。目の前で仕上がるひと皿を、最初の一杯と。</p></article><article class="taste reveal">{photo_figure("food-vegetables","彩り豊かに盛り付けたひよりの野菜料理",cls="taste-media")}<span class="taste-num">02 / OYASAI</span><h3>お野菜に、ひと工夫。</h3><p>トマトに削り鰹とはちみつ。ナスに鯛味噌とマスカルポーネ。いつもの野菜に、新しい出会いを。</p></article><article class="taste reveal">{optional_clip("riceVideo","炊き立ての土鍋ご飯") or photo_figure("food-rice","黒い土鍋で炊き上げた白いご飯",cls="taste-media")}<span class="taste-num">03 / DONABE</span><h3>最後は、炊き立てを。</h3><p>土鍋で炊いた白いご飯に、ご飯のお供を少しずつ。もう少しだけ、この時間を楽しみたくなる締めくくり。</p></article></div><a class="text-link" href="/menu.html">お料理をくわしく<span class="arrow" aria-hidden="true">→</span></a></div></section>
<section class="vegetables wrap"><div class="veg-title reveal"><div class="section-number">ひよりのひと工夫</div><h2>お野菜って、<br>こんなに楽しい。</h2><p>素材と素材が出会う、<br>ひよりならではの組み合わせ。</p><svg class="veg-illustration" viewBox="0 0 160 140" aria-hidden="true"><path d="M45 50c-38-10-39 51-12 61 14 5 28 0 33-14 18-30 10-50-21-47Z M42 54l-8-15 14 7 10-15 1 16 16 3-18 6 M48 46c-4-12-4-18 4-25 M88 89c4-30 23-42 37-30 17 17-4 48-31 56-16 6-23-1-6-26Z M113 62l-8-9 16 1 10-13 1 15 12 5-17 5 M123 53c2-11 6-15 12-18"/></svg></div><div class="veg-list reveal"><ul><li><span class="index">01</span><span class="ingredient">トマト</span><span class="times">×</span><span class="pairing">削り鰹 × はちみつ</span></li><li><span class="index">02</span><span class="ingredient">ナス</span><span class="times">×</span><span class="pairing">鯛味噌 × マスカルポーネ</span></li><li><span class="index">03</span><span class="ingredient">ジャガ</span><span class="times">×</span><span class="pairing">ゆずごしょうバター × 炭レモン</span></li><li><span class="index">04</span><span class="ingredient">さつまいも</span><span class="times">×</span><span class="pairing">黒ゴマ × キナコ</span></li></ul><a class="text-link" href="/menu.html#category-1">ほかのお野菜も見る<span class="arrow" aria-hidden="true">→</span></a></div><div class="veg-gallery">{photo_figure("creative-01","イチジクを添えた彩り豊かなひと皿",cls="reveal")}{photo_figure("creative-02","黒い器に盛り付けたひよりのひと皿",cls="reveal")}{photo_figure("creative-03","白い角皿に盛り付けた香ばしいひと皿",cls="reveal")}</div></section>
<section class="drink-feature wrap" id="drinks"><div class="drink-heading"><div class="reveal"><div class="section-number">ひよりのお飲み物</div><h2>ひと皿に、<br>寄り添う一杯。</h2></div><div class="reveal"><p>果実とハーブのサワーに、日本酒、ワイン。<br>お料理と、その日の気分に合わせて。</p><a class="text-link" href="/drink.html">お飲み物をくわしく<span class="arrow" aria-hidden="true">→</span></a></div></div><div class="drink-photo-grid">{photo_figure("sour","大葉を添えた爽やかなサワー","爽やかなサワー。",cls="reveal")}{photo_figure("shochu","CHILL GREENのボトルと氷を満たしたグラス","香りを楽しむ焼酎。",cls="reveal")}{photo_figure("highball","デュワーズのボトルとハイボール","お好きなハイボールも。",cls="reveal")}</div></section>
<section class="room-section wrap" id="space"><div class="room-top reveal"><div><div class="section-number">お席と空間</div><h2>それぞれの、くつろぎ。</h2></div><p>木の温もり、柔らかな灯り。<br>カウンターでも、テーブルでも、お座敷でも。<br>今夜の気分に合うお席で。</p></div><div class="room-display reveal"><div class="room-picture">{image("counter","厨房で料理を仕上げるスタッフと、ひよりの木のカウンター席","photo-counter",image_id="room-image")}</div><div class="room-detail"><div class="room-tabs" role="tablist" aria-label="席の種類"><button id="tab-counter" role="tab" aria-selected="true" aria-controls="room-panel" data-room="counter">カウンター</button><button id="tab-table" role="tab" aria-selected="false" aria-controls="room-panel" tabindex="-1" data-room="table">テーブル</button><button id="tab-tatami" role="tab" aria-selected="false" aria-controls="room-panel" tabindex="-1" data-room="tatami">お座敷</button></div><div id="room-panel" role="tabpanel" aria-labelledby="tab-counter" aria-live="polite"><div class="eyebrow" id="room-en">AT THE COUNTER</div><h3 id="room-title">手仕事が見える、特等席。</h3><p id="room-text">料理が仕上がる音や香りも、ごちそうのひとつ。オープンキッチンを目の前に、思い思いの一杯を。</p></div><a class="text-link" href="/space.html">店内をもっと見る<span class="arrow" aria-hidden="true">→</span></a></div></div></section>
<section class="news-section wrap"><h2>ひより便り</h2><div id="home-news">{home_news}</div></section>'''

restaurant = {'@context':'https://schema.org','@type':'Restaurant','name':cfg['name'],'servesCuisine':['和食','居酒屋'],'address':{'@type':'PostalAddress','addressCountry':'JP','addressRegion':'福岡県','addressLocality':'福岡市中央区','streetAddress':'渡辺通5丁目24-37 2F'}}
if cfg['telephone']: restaurant['telephone'] = cfg['telephone']
if site_url: restaurant.update({'url':site_url+'/', 'menu':site_url+'/menu.html','image':site_url+'/images/room-1800.webp'})
write_page('/', '肴とお野菜 ひより｜天神南・渡辺通の和食居酒屋', '福岡・天神南の「肴とお野菜 ひより」。お席で仕上げるサワラの藁焼き、ひと工夫の野菜料理、炊き立て土鍋ご飯。木の温もりに包まれるカウンター・テーブル・お座敷で、くつろぎのひとときを。', home, home=True, extra='<script type="application/ld+json">'+json.dumps(restaurant,ensure_ascii=False)+'</script><script src="/blog/news.js" defer></script>')

def sub_intro(en, title, text):
    return f'<div class="wrap"><div class="breadcrumb"><a href="/">ひより</a><span aria-hidden="true">/</span><span>{title}</span></div><section class="sub-intro"><div><div class="eyebrow">{en}</div><h1>{title}</h1></div><p>{text}</p></section></div>'

for section,path,title,en,desc in [('FOOD','/menu.html','お料理','SEASONAL FOOD','香ばしい肴と、ひと工夫のお野菜。<br>お好きなものを、少しずつ。'),('DRINK','/drink.html','お飲み物','A GLASS FOR YOUR EVENING','日本酒、ワイン、果実とハーブのサワー。<br>今日のひと皿に合わせて、お好きな一杯を。')]:
    cats=[(i,c) for i,c in enumerate(menus) if c['section']==section]
    body=sub_intro(en,title,desc) + '<div class="wrap"><nav class="menu-categories" aria-label="お品書きの分類">' + ''.join(f'<a href="#category-{i}">{esc(c["name"])}</a>' for i,c in cats) + '</nav><p class="menu-note">仕入れや季節により、内容が変わることがございます。</p><div class="menu-columns">'
    for i,c in cats:
        body += f'<section class="menu-category" id="category-{i}"><h2>{esc(c["name"])}</h2><ul class="menu-items">'
        for item in c['items']:
            body+=f'<li><span>{esc(item["name"])}</span><span class="price">{item["price"]:,}円</span></li>'
        body+='</ul></section>'
    other='/drink.html' if section=='FOOD' else '/menu.html'
    other_label='お飲み物を見る' if section=='FOOD' else 'お料理を見る'
    body+=f'</div><div class="menu-switch"><a class="text-link" href="{other}">{other_label}<span class="arrow" aria-hidden="true">→</span></a></div></div>'
    write_page(path,f'{title}｜肴とお野菜 ひより｜天神南',f'肴とお野菜 ひよりの{title}。'+re.sub('<[^>]+>','',desc),body)

space_body=sub_intro('A PLACE TO UNWIND','お席と空間','ひとりで、ふたりで、みんなで。<br>その日の気分に寄り添う、ひよりのお席。')+'<div class="wrap space-stories">'
for im,en,title,copy in [('counter','01 / COUNTER','手仕事が見える、特等席。','目の前は、オープンキッチン。仕上がる料理を眺めながら、ひと皿と一杯をゆっくりと。'),('table','02 / TABLE','顔を合わせて、ゆっくりと。','木のテーブルを囲んで、お皿を分け合う。気の合う人と過ごす夜に、柔らかな灯りのお席を。'),('tatami','03 / TATAMI','靴をぬいで、ひと息。','木の間仕切りに囲まれた、落ち着いたお座敷。いつもより少し長く、話していたくなる場所。')]:
    alt={'counter':'厨房を目の前にした木のカウンター席','table':'木の格子と照明が温かなテーブル席','tatami':'座布団と低いテーブルを備えたお座敷'}[im]
    space_body+=f'<section class="space-story reveal"><div class="space-story-photo">{image("counter",alt,"photo-counter") if im == "counter" else photo("dining" if im == "table" else im,alt)}</div><div><div class="eyebrow">{en}</div><h2>{title}</h2><p>{copy}</p></div></section>'
space_body+='</div>'
write_page('/space.html','お席と空間｜肴とお野菜 ひより｜天神南', 'ひよりの店内をご紹介。調理風景を楽しむカウンター、木のテーブル席、落ち着いたお座敷をご用意しています。',space_body)

faqs=[('どのような料理がありますか？','お席で仕上げるサワラの藁焼き、トマトやナスなどの創作野菜料理、炊き立ての土鍋ご飯をご用意しています。'),('どのような席がありますか？','カウンター席、テーブル席、お座敷がございます。店内の雰囲気は「お席と空間」のページでご覧いただけます。'),('お店はどこにありますか？',cfg['address']+'にございます。Googleの店舗情報もあわせてご確認ください。')]
access_body=sub_intro('COME ON IN','ご来店案内','いい日も、なんでもない日も。<br>暖簾の向こうで、お待ちしています。')+f'<div class="wrap"><section class="access-page"><div>{photo_figure("entrance","木の看板と格子戸が目印のひよりの入口","この看板を目印に、お越しください。","entrance-photo")}</div><div>{details()}{visit_links()}<p class="menu-note">最新の営業情報は、Googleの店舗情報をご確認ください。</p></div></section><section class="faq"><h2>よくあるご質問</h2>'+''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in faqs)+'</section></div>'
faq_schema={'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in faqs]}
write_page('/access.html','ご来店案内｜肴とお野菜 ひより｜福岡市中央区渡辺通', '肴とお野菜 ひよりの店舗情報。福岡市中央区渡辺通5丁目24-37 2F。ご来店の前に店内・お料理・Googleの最新情報をご確認ください。',access_body,full_footer=False,extra='<script type="application/ld+json">'+json.dumps(faq_schema,ensure_ascii=False)+'</script>')

news_body=sub_intro('LETTERS FROM HIYORI','ひより便り','お店からの、小さなお知らせ。')+'<div class="wrap"><section class="journal"><div class="post-list" id="post-list">'+''.join(f'<a href="/blog/posts/post.html?slug={quote(p["slug"])}"><time datetime="{esc(p["date"])}">{esc(p["date"])}</time><h2>{esc(p["title"])}</h2><p>{esc(p["excerpt"])}</p></a>' for p in posts)+'</div></section></div>'
write_page('/blog/','ひより便り｜肴とお野菜 ひより','天神南・渡辺通の「肴とお野菜 ひより」からのお知らせ。',news_body,extra='<script src="/blog/news.js" defer></script>')
post_body='<div class="wrap"><div class="breadcrumb"><a href="/">ひより</a><span>/</span><a href="/blog/">ひより便り</a></div><article class="journal article-layout" id="post-content" aria-live="polite"><p>お便りを読み込んでいます。</p><noscript><p>記事の表示にはJavaScriptが必要です。<a href="/blog/">お便り一覧はこちら</a>。</p></noscript></article></div>'
post_extra='<link rel="stylesheet" href="/blog/article.css"><script src="/vendor/dompurify/purify.min.js" defer></script><script src="/vendor/blog-security.js" defer></script><script src="/vendor/marked/marked.umd.js" defer></script><script src="/blog/post.js" defer></script>'
write_page('/blog/posts/post.html','ひより便り｜肴とお野菜 ひより','肴とお野菜 ひよりからのお便り。',post_body,extra=post_extra)

robots = 'User-agent: *\n' + ('Allow: /\n' if indexable else 'Disallow: /\n')
if site_url: robots += f'Sitemap: {site_url}/sitemap.xml\n'
(ROOT/'robots.txt').write_text(robots)
if site_url:
    urls=['/','/menu.html','/drink.html','/space.html','/access.html','/blog/']+[f'/blog/posts/post.html?slug={quote(p["slug"])}' for p in posts]
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+esc(site_url+u)+'</loc></url>' for u in urls)+'</urlset>')
elif (ROOT/'sitemap.xml').exists():
    (ROOT/'sitemap.xml').unlink()
(ROOT/'.nojekyll').touch()
print(f'Built 7 static pages, {sum(len(c["items"]) for c in menus)} menu items; site URL: {site_url or "local preview"}; indexable: {indexable}')
