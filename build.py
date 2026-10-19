#!/usr/bin/env python3
"""Сборка статического сайта panagro.kz.

python3 build.py prod    -> dist/      (чистые URL, Google Analytics)
python3 build.py preview -> preview/   (ссылки на index.html, без аналитики — для просмотра в артефакте)
"""
import html, json, os, posixpath, re, shutil, sys, urllib.parse
from datetime import date

from pages import PAGES, NAV, FOOTER_NAV, SITE

MODE = sys.argv[1] if len(sys.argv) > 1 else "prod"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT_DIR") or os.path.join(ROOT, "..", "dist" if MODE == "prod" else "preview")
BASE = SITE["base"]
GA_ID = SITE["ga4"]
YM_ID = SITE.get("metrika")
WA = SITE["wa_number"]
E = html.escape


def wa_link(text=""):
    return f"https://wa.me/{WA}" + (f"?text={urllib.parse.quote(text)}" if text else "")


def file_of(url):
    return url.strip("/") + "/index.html" if url.strip("/") else "index.html"


def rel(cur_url, target):
    """Относительная ссылка с cur_url на target (target — путь сайта или ассет)."""
    if target.startswith(("http", "#", "mailto:", "tel:")):
        return target
    frag = ""
    if "#" in target:
        target, frag = target.split("#", 1)
        frag = "#" + frag
    cur_dir = posixpath.dirname(file_of(cur_url))
    if target.endswith("/"):
        dest = file_of(target)
        r = posixpath.relpath(dest, cur_dir or ".")
        if MODE == "prod":
            r = r[: -len("index.html")] or "./"
    else:
        r = posixpath.relpath(target.lstrip("/"), cur_dir or ".")
    return r + frag


WA_SVG = ('<svg class="wa" viewBox="0 0 32 32" aria-hidden="true"><path fill="currentColor" d="M16 3C8.8 3 3 8.7 3 15.8c0 2.5.7 4.9 2 7L3 29l6.4-2c2 1.1 4.3 1.7 6.6 1.7 7.2 0 13-5.7 13-12.8S23.2 3 16 3zm0 23.4c-2.1 0-4.1-.6-5.9-1.6l-.4-.3-3.8 1.2 1.2-3.7-.3-.4a10.4 10.4 0 0 1-1.7-5.8C5.1 9.9 10 5.2 16 5.2s10.9 4.7 10.9 10.6S22 26.4 16 26.4zm6-7.9c-.3-.2-1.9-.9-2.2-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7.1a8.8 8.8 0 0 1-4.4-3.8c-.3-.6.3-.5 1-1.7.1-.2 0-.4 0-.5l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4s-1.2 1.1-1.2 2.7 1.2 3.2 1.4 3.4 2.4 3.6 5.8 5c2.2.9 3 1 4.1.8.7-.1 1.9-.8 2.2-1.5s.3-1.4.2-1.5-.3-.2-.6-.3z"/></svg>')
TOWER = open(os.path.join(ROOT, "assets/img/panagro-mark.svg")).read()


# ---------- компоненты ----------

def btn(cur, label, href, kind="amber", wa_text=None):
    if wa_text is not None or href == "wa":
        return f'<a class="btn btn-{kind}" target="_blank" rel="noopener" href="{E(wa_link(wa_text or ""))}">{E(label)}</a>'
    return f'<a class="btn btn-{kind}" href="{E(rel(cur, href))}">{E(label)}</a>'


def render_cta(cur, ctas):
    out = []
    for i, c in enumerate(ctas or []):
        kind = c.get("kind", "amber" if i == 0 else "ghost")
        out.append(btn(cur, c["label"], c.get("href", "wa"), kind, c.get("wa")))
    return f'<div class="cta-row">{"".join(out)}</div>' if out else ""


def section(p, s):
    cur = p["url"]
    t = s["type"]
    cls = ' class="alt"' if s.get("alt") else ""
    sid = f' id="{s["id"]}"' if s.get("id") else ""
    head = ""
    if s.get("h2"):
        head = '<div class="sec-head">'
        if s.get("eyebrow"):
            head += f'<p class="eyebrow">{E(s["eyebrow"])}</p>'
        head += f'<h2>{E(s["h2"])}</h2>'
        if s.get("intro"):
            head += f'<p>{s["intro"]}</p>'
        head += "</div>"
    body = ""
    if t == "bullets":
        items = "".join(f"<li><p><b>{E(b)}</b>{(' — <span>' + x + '</span>') if x else ''}</p></li>" for b, x in s["items"])
        body = f'<ul class="bullets">{items}</ul>'
    elif t == "cards":
        n = s.get("cols", 3)
        items = []
        for it in s["items"]:
            tag = f'<span class="tag">{E(it["tag"])}</span>' if it.get("tag") else ""
            inner = f'{tag}<h3>{E(it["title"])}</h3><p>{it["text"]}</p>'
            if it.get("href"):
                items.append(f'<a class="card" href="{E(rel(cur, it["href"]))}">{inner}</a>')
            else:
                items.append(f'<div class="card">{inner}</div>')
        body = f'<div class="cards c{n}">{"".join(items)}</div>'
    elif t == "table":
        th = "".join(f'<th scope="col">{E(h)}</th>' for h in s["head"])
        rows = "".join("<tr>" + "".join((f'<th scope="row">{c}</th>' if j == 0 else f"<td>{c}</td>") for j, c in enumerate(r)) + "</tr>" for r in s["rows"])
        note = f'<p class="tbl-note">{s["note"]}</p>' if s.get("note") else ""
        body = f'<div class="tbl-wrap"><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>{note}'
    elif t == "steps":
        items = "".join(f"<li><h3>{E(a)}</h3><p>{b}</p></li>" for a, b in s["items"])
        body = f'<ol class="steps">{items}</ol>'
    elif t == "prose":
        body = '<div class="prose">' + "".join(f"<p>{x}</p>" for x in s["paras"]) + "</div>"
    elif t == "faq":
        body = '<div class="faq">' + "".join(f"<details><summary>{E(q)}</summary><p>{a}</p></details>" for q, a in s["items"]) + "</div>"
    elif t == "links":
        body = '<div class="blog-list">' + "".join(
            f'<a href="{E(rel(cur, h))}"{" target=_blank rel=noopener" if h.startswith("http") else ""}><small>{E(m)}</small><h3>{E(ti)}</h3></a>' for ti, m, h in s["items"]) + "</div>"
    elif t == "html":
        body = re.sub(r"@@IMG:([^@]+)@@", lambda m: rel(cur, "/assets/img/" + m.group(1)), s["html"])
    elif t == "cta":
        body = (f'<div class="cta-band"><div><h2>{E(s["title"])}</h2>' + (f'<p>{E(s["text"])}</p>' if s.get("text") else "") +
                f'</div>{render_cta(cur, s["ctas"])}</div>')
        return f'<section{sid}{cls}><div class="wrap">{body}</div></section>'
    after = render_cta(cur, s.get("ctas"))
    return f'<section{sid}{cls}><div class="wrap">{head}{body}{after}</div></section>'


def hero(p):
    cur = p["url"]
    crumbs = ""
    if p.get("crumbs"):
        parts = [f'<a href="{rel(cur, "/")}">Главная</a>']
        for name, url in p["crumbs"]:
            parts.append('<span aria-hidden="true">/</span>')
            parts.append(f'<a href="{rel(cur, url)}">{E(name)}</a>' if url else f"<span>{E(name)}</span>")
        crumbs = f'<nav class="crumbs" aria-label="Хлебные крошки">{"".join(parts)}</nav>'
    img = p.get("img")
    if img:
        fig = (f'<figure class="scheme" style="margin:0"><img class="hero-photo" src="{rel(cur, "/assets/img/" + img[0])}" '
               f'alt="{E(img[1])}" width="1200" height="800">' + (f"<figcaption>{E(img[2])}</figcaption>" if len(img) > 2 else "") + "</figure>")
    elif p.get("placeholder"):
        fig = f'<div class="ph"><div>{TOWER}<br>{E(p["placeholder"])}</div></div>'
    else:
        fig = ""
    lead = f'<p class="lead">{p["lead"]}</p>' if p.get("lead") else ""
    eyebrow = f'<p class="eyebrow" style="color:var(--band-muted)">{E(p["eyebrow"])}</p>' if p.get("eyebrow") else ""
    return (f'<section class="page-hero{"" if fig else " noimg"}"><div class="wrap"><div class="hero-grid"><div>{crumbs}{eyebrow}'
            f'<h1 style="margin-top:10px">{E(p["h1"])}</h1>{lead}{render_cta(cur, p.get("ctas"))}</div>{fig}</div></div></section>')


def jsonld(p):
    data = [{
        "@context": "https://schema.org", "@type": "LocalBusiness", "name": "PANAGRO service",
        "legalName": "ТОО «PANAGRO service»", "url": BASE + "/", "logo": BASE + "/assets/img/panagro-logo.svg",
        "telephone": "+77771138433", "email": "info@panagro.kz", "foundingDate": "2020",
        "address": {"@type": "PostalAddress", "streetAddress": "Илийский тракт, 7", "addressLocality": "Алматы", "addressCountry": "KZ"},
        "areaServed": ["Алматинская область", "Жетысуская область", "Жамбылская область", "Туркестанская область", "Кызылординская область"],
        "openingHours": "Mo-Fr 09:00-18:00",
    }]
    if p.get("crumbs"):
        items = [{"@type": "ListItem", "position": 1, "name": "Главная", "item": BASE + "/"}]
        for i, (name, url) in enumerate(p["crumbs"], 2):
            items.append({"@type": "ListItem", "position": i, "name": name, "item": BASE + (url or p["url"])})
        data.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})
    faqs = [s for s in p.get("sections", []) if s["type"] == "faq"]
    if faqs:
        import re
        data.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for s in faqs for q, a in s["items"]]})
    return "".join(f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>' for d in data)


def layout(p, main_html):
    cur = p["url"]
    a = lambda path: rel(cur, path)
    canonical = BASE + cur
    ga = ""
    if MODE == "prod" and GA_ID:
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>'
              f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>")
    if MODE == "prod" and YM_ID:  # METRIKA
        ga += (f'<script>(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};m[i].l=1*new Date();'
               f'for(var j=0;j<document.scripts.length;j++){{if(document.scripts[j].src===r){{return;}}}}'
               f'k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})'
               f'(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");'
               f'ym({YM_ID},"init",{{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true}});window.YM_ID={YM_ID};</script>'
               f'<noscript><div><img src="https://mc.yandex.ru/watch/{YM_ID}" style="position:absolute;left:-9999px" alt=""></div></noscript>')
    verif = "".join(f'<meta name="{k}" content="{E(v)}">' for k, v in SITE.get("verification", {}).items() if v)
    nav = "".join(f'<a href="{a(u)}"{" aria-current=page" if cur.startswith(u) and u != "/" else ""}>{E(n)}</a>' for n, u in NAV)
    mnav = "".join(f'<a href="{a(u)}">{E(n)}</a>' for n, u in NAV)
    fnav = "".join(f'<a href="{a(u)}">{E(n)}</a>' for n, u in FOOTER_NAV)
    logo_white = open(os.path.join(ROOT, "assets/img/panagro-logo-white.svg")).read().replace("<svg ", '<svg class="logo" ', 1)
    og_img = BASE + "/assets/img/" + (p.get("img") or ["panazoo-parallel-2x20.webp"])[0]
    robots = '<meta name="robots" content="noindex">' if p.get("noindex") or MODE != "prod" else ""
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(p["title"])}</title>
<meta name="description" content="{E(p["desc"])}">
<link rel="canonical" href="{canonical}">
{robots}{verif}
<meta property="og:type" content="website"><meta property="og:locale" content="ru_KZ"><meta property="og:site_name" content="PANAGRO">
<meta property="og:title" content="{E(p["title"])}"><meta property="og:description" content="{E(p["desc"])}">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{og_img}">
<link rel="icon" type="image/svg+xml" href="{a("/assets/img/panagro-mark.svg")}">
<link rel="icon" type="image/png" sizes="32x32" href="{a("/assets/img/favicon-32.png")}">
<link rel="apple-touch-icon" href="{a("/assets/img/favicon-180.png")}">
<meta name="theme-color" content="#144D29">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@500;600;700&family=Golos+Text:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap">
<link rel="stylesheet" href="{a("/assets/site.css")}">
{ga}{jsonld(p)}
</head>
<body>
<header class="top"><div class="wrap">
<a class="logo-link" href="{a("/")}" aria-label="PANAGRO — на главную">{logo_white}</a>
<nav class="nav" aria-label="Главное меню">{nav}</nav>
<a class="phone" href="tel:+77771138433" style="color:inherit;text-decoration:none">+7 777 113 84 33</a>
<details class="mnav"><summary>Меню</summary><div class="mnav-list">{mnav}</div></details>
<a class="btn btn-amber" href="{wa_link()}" target="_blank" rel="noopener">{WA_SVG}<span>WhatsApp</span></a>
</div></header>
<main>
{main_html}
</main>
<footer><div class="wrap">
{logo_white}
<div>ТОО «PANAGRO service»<br>Алматы, Илийский тракт, 7<br>+7 777 113 84 33 · +7 (727) 973-22-56<br>info@panagro.kz<br>Офис: пн–пт 9:00–18:00 · аварийные заявки 24/7</div>
<nav class="footer-nav" aria-label="Разделы сайта">{fnav}<a href="https://pana.kz/" target="_blank" rel="noopener">Магазин запчастей pana.kz</a></nav>
</div></footer>
<a class="float-wa" href="{wa_link()}" target="_blank" rel="noopener" aria-label="Написать в WhatsApp">{WA_SVG.replace('class="wa"', 'style="width:30px;height:30px;color:#fff"')}</a>
<script src="{a("/assets/site.js")}" defer></script>
</body>
</html>
"""


def build_page(p):
    if p.get("raw"):
        main_html = p["raw"](lambda path: rel(p["url"], path), wa_link)
    else:
        main_html = hero(p) + "".join(section(p, s) for s in p.get("sections", []))
    return layout(p, main_html)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    for p in PAGES:
        path = os.path.join(OUT, file_of(p["url"]))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").write(build_page(p))
    today = date.today().isoformat()
    urls = "".join(f"<url><loc>{BASE}{p['url']}</loc><lastmod>{today}</lastmod></url>" for p in PAGES if not p.get("noindex"))
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n" if MODE == "prod" else "User-agent: *\nDisallow: /\n")
    if MODE == "prod":
        open(os.path.join(OUT, ".htaccess"), "w").write(open(os.path.join(ROOT, "htaccess.txt")).read())
    print(f"{MODE}: {len(PAGES)} pages -> {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
