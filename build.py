# -*- coding: utf-8 -*-
"""Builds the MeraLawyer.pk static website into ./site . Run: python3 build.py"""
import json, os, re, shutil, html, urllib.parse
from content import CONFIG as C, AREAS, SERVICES, CITIES, COURTS, GENERAL_FAQS, CEO

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
D = C["domain"]
E = lambda s: html.escape(str(s), quote=True)
A_BY = {a["slug"]: a for a in AREAS}
S_BY = {s["slug"]: s for s in SERVICES}
PAGES = []  # (path, title, description) for sitemap / llms

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

# ------------------------------------------------------------------ icons
P = {
 "scale": "M12 3v18 M7 21h10 M4 7h16 M4 7l-2.5 6a3 3 0 0 0 5 0L4 7z M20 7l-2.5 6a3 3 0 0 0 5 0L20 7z",
 "check": "M5 12l5 5L20 7", "chev": "M9 6l6 6-6 6", "plus": "M12 5v14 M5 12h14",
 "lock": "M5 11h14v10H5z M8 11V7a4 4 0 0 1 8 0v4",
 "shield": "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z M9 12l2 2 4-4",
 "wa": "M3 21l1.7-5A8.5 8.5 0 1 1 8 19.3L3 21z M9 9.5c.3 2.2 2.3 4.3 4.5 4.8l1.2-1.2 2 1-.6 1.6c-3.6.4-7.7-3.6-7.4-7.3l1.6-.6 1 2-1.3 1.2",
 "phone": "M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z",
 "rupee": "M6 4h12 M6 9h12 M6 4h4a5 5 0 0 1 0 10H6l9 7",
 "chat": "M4 4h16v12H8l-4 4z", "menu": "M4 7h16 M4 12h16 M4 17h16",
 "family": "M9 7a3 3 0 1 1 0 6 3 3 0 0 1 0-6z M3 21a6 6 0 0 1 12 0 M17 8a3 3 0 1 1 0 6 M21 21a6 6 0 0 0-4-5.6",
 "gavel": "M14 4l6 6 M11 7l6 6 M12.5 5.5l-7 7 3 3 7-7 M3 21h10",
 "home": "M3 21h18 M5 21V10l7-6 7 6v11 M10 21v-6h4v6",
 "bldg": "M3 21V8l9-5 9 5v13 M9 21v-7h6v7 M3 21h18",
 "globe": "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M2 12h20 M12 2c3 3 3 17 0 20 M12 2c-3 3-3 17 0 20",
 "calc": "M5 2h14v20H5z M8 6h8v4H8z M8 14h2 M14 14h2 M8 18h2 M14 18h2",
 "receipt": "M5 2h14v20l-3-2-2 2-2-2-2 2-2-2-3 2z M9 7h6 M9 11h6 M9 15h4",
 "pct": "M19 5L5 19 M7 5a2 2 0 1 0 0 4 2 2 0 0 0 0-4z M17 15a2 2 0 1 0 0 4 2 2 0 0 0 0-4z",
 "star": "M12 3l2.6 5.5 6 .8-4.4 4.2 1 6L12 16.6 6.8 19.5l1-6L3.4 9.3l6-.8z",
 "mail": "M4 4h16v16H4z M4 4l8 8 8-8", "doc": "M6 2h9l5 5v15H6z M14 2v6h6 M9 13h8 M9 17h6",
 "rings": "M8 14a5 5 0 1 0 0-.1 M16 14a5 5 0 1 0 0-.1",
 "search": "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14z M21 21l-5-5",
 "key": "M14 3a6 6 0 1 1-4.5 10L3 19.5V22h3v-2h2v-2h2l1.5-1.5A6 6 0 0 1 14 3z",
 "user": "M12 3a4 4 0 1 1 0 8 4 4 0 0 1 0-8z M4 21a8 8 0 0 1 16 0",
 "split": "M12 3v6 M12 9l-6 6v6 M12 9l6 6v6",
 "x": "M6 6l12 12 M18 6L6 18",
}
AREA_ICON = {"family-lawyer": "family", "criminal-lawyer": "gavel", "property-lawyer": "home", "corporate-lawyer": "bldg", "overseas-pakistani-lawyer": "globe"}
SVC_ICON = {"company-registration": "bldg", "income-tax-return": "calc", "ntn-registration": "receipt", "sales-tax-registration": "pct", "trademark-registration": "star", "legal-notice": "mail", "agreements": "doc", "court-marriage": "rings", "khula": "split", "succession-certificate": "family", "property-verification": "search", "property-transfer": "key", "power-of-attorney": "user", "bail-application": "gavel"}

def icon(name, size=24, color="currentColor", sw=1.7, cls=""):
    d = " ".join('<path d="%s"/>' % ("M" + seg if not seg.startswith("M") else seg) for seg in P[name].split(" M"))
    return ('<svg%s width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="%s" stroke-width="%s" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">%s</svg>') % (
            (' class="%s"' % cls) if cls else "", size, size, color, sw, d)

GOLD = "#C8A24A"
TICK = icon("check", 18, GOLD, 2.2)
WA_URL = "https://wa.me/" + C["whatsapp"]
TEL = "tel:" + C["phone"].replace("-", "")

# ------------------------------------------------------------------ fonts (Urdu subset)
URDU_TEXT = "میرا وکیل، حق انصاف" + "".join(a["urdu"] for a in AREAS) + "".join(c["urdu"] for c in CITIES) + "اردو" + CEO["urdu"]
URDU_FONT = "https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@700&display=swap&text=" + urllib.parse.quote("".join(sorted(set(URDU_TEXT))))
LATIN_FONT = "https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,500..700;1,6..96,400..600&family=Figtree:wght@400;500;600;700&display=swap"

# ------------------------------------------------------------------ schema
def org_node():
    same = [u for u in (C["facebook"], C["instagram"], C["linkedin"], C["youtube"]) if u]
    def place(city, region, lat, lng, addr):
        return {"@type": "PostalAddress", "streetAddress": addr, "addressLocality": city, "addressRegion": region, "addressCountry": "PK"}
    catalog = [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": "%s/legal-services/%s/" % (D, s["slug"])}} for s in SERVICES]
    n = {
        "@type": ["LegalService", "Organization"], "@id": D + "/#org",
        "name": C["brand"], "alternateName": ["Mera Lawyer", "میرا وکیل", "MeraLawyer"],
        "url": D + "/", "logo": D + "/assets/img/logo.png", "image": D + "/assets/img/og-image.png",
        "description": "MeraLawyer.pk helps people hire vetted lawyers in Islamabad and Rawalpindi and provides legal services such as company registration, tax return filing, legal notices, court marriage, khula and property transfer.",
        "telephone": C["phone"], "email": C["email"], "priceRange": "Rs",
        "foundingDate": C["founded"], "knowsLanguage": ["en", "ur"],
        "address": place("Islamabad", "Islamabad Capital Territory", "33.6844", "73.0479", C["isb_address"]),
        "geo": {"@type": "GeoCoordinates", "latitude": 33.6844, "longitude": 73.0479},
        "areaServed": [{"@type": "City", "name": "Islamabad"}, {"@type": "City", "name": "Rawalpindi"}, {"@type": "Country", "name": "Pakistan"}],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "opens": "09:00", "closes": "19:00"}],
        "contactPoint": [{"@type": "ContactPoint", "telephone": C["phone"], "contactType": "customer service", "areaServed": "PK", "availableLanguage": ["English", "Urdu"]}],
        "knowsAbout": ["Family law in Pakistan", "Khula", "Criminal law", "Bail", "Property law", "Company registration with SECP", "Income tax return filing with FBR", "Sales tax", "Trademark registration", "Succession certificate", "Court marriage"],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Legal services", "itemListElement": catalog},
        "department": [{"@type": "LegalService", "@id": D + "/#rawalpindi", "name": C["brand"] + " Rawalpindi", "telephone": C["phone"],
                        "address": place("Rawalpindi", "Punjab", "33.5651", "73.0169", C["rwp_address"]),
                        "geo": {"@type": "GeoCoordinates", "latitude": 33.5651, "longitude": 73.0169}, "url": D + "/lawyer-in-rawalpindi/"}],
    }
    if same: n["sameAs"] = same
    n["founder"] = {"@id": D + "/about/" + CEO["slug"] + "/#person"}
    n["employee"] = [{"@id": D + "/about/" + CEO["slug"] + "/#person"}]
    return n

def graph(path, title, desc, crumbs, ptype="WebPage", extra=None, faqs=None):
    url = D + path
    nodes = [org_node(),
             {"@type": "WebSite", "@id": D + "/#website", "url": D + "/", "name": C["brand"], "inLanguage": "en-PK", "publisher": {"@id": D + "/#org"}}]
    page = {"@type": ptype, "@id": url + "#webpage", "url": url, "name": title, "description": desc, "inLanguage": "en-PK",
            "isPartOf": {"@id": D + "/#website"}, "about": {"@id": D + "/#org"}, "dateModified": C["updated"],
            "primaryImageOfPage": {"@type": "ImageObject", "url": D + "/assets/img/og-image.png"},
            "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["h1", ".answer p"]}}
    if crumbs:
        page["breadcrumb"] = {"@id": url + "#breadcrumb"}
        nodes.append({"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": D + p} for i, (n, p) in enumerate(crumbs)]})
    if ptype != "WebPage" or path != "/":
        page["reviewedBy"] = {"@type": "Person", "name": C["reviewer"]}
        page["lastReviewed"] = C["updated"]
    nodes.append(page)
    if faqs:
        nodes.append({"@type": "FAQPage", "@id": url + "#faq", "isPartOf": {"@id": url + "#webpage"}, "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})
    nodes += extra or []
    return json.dumps({"@context": "https://schema.org", "@graph": nodes}, ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ shared chunks
def head(path, title, desc, schema, og_type="website", noindex=False):
    url = D + path
    robots = "noindex, follow" if noindex else "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
    return f"""<!doctype html>
<html lang="en-PK" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{robots}">
<link rel="alternate" hreflang="en-PK" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta name="author" content="{E(C['brand'])}">
<meta name="theme-color" content="#0D2B26">
<meta name="geo.region" content="PK-IS">
<meta name="geo.placename" content="Islamabad, Rawalpindi">
<meta name="geo.position" content="33.6844;73.0479">
<meta name="ICBM" content="33.6844, 73.0479">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{E(C['brand'])}">
<meta property="og:locale" content="en_PK">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{D}/assets/img/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="MeraLawyer.pk, hire a lawyer in Islamabad and Rawalpindi">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{D}/assets/img/og-image.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="text/plain" title="LLM summary" href="/llms.txt">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{E(LATIN_FONT)}">
<link rel="stylesheet" href="{E(URDU_FONT)}">
<link rel="stylesheet" href="/assets/css/styles.css">
<script type="application/ld+json">
{schema}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""

def header(active=""):
    def cur(k): return ' aria-current="page"' if active == k else ""
    areas = "".join(f'<a href="/hire-a-lawyer/{a["slug"]}/">{E(a["name"])}</a>' for a in AREAS)
    top = ["company-registration", "income-tax-return", "ntn-registration", "trademark-registration", "khula", "court-marriage", "succession-certificate", "property-transfer"]
    svcs = "".join(f'<a href="/legal-services/{s}/">{E(S_BY[s]["name"])}</a>' for s in top)
    return f"""<div class="topbar"><div class="wrap">
<div class="live"><span class="dot" aria-hidden="true"></span><span>Lawyers available today in Islamabad and Rawalpindi</span></div>
<div class="topbar-links"><a href="{TEL}">Call {E(C['phone_display'])}</a><a href="mailto:{E(C['email'])}">{E(C['email'])}</a><span>{E(C['hours_display'])}</span></div>
</div></div>
<header class="site-header"><div class="wrap">
<a class="logo" href="/" aria-label="{E(C['brand'])} home">
<span class="logo-mark">{icon('scale', 24, GOLD, 1.6)}</span>
<span><span class="logo-name">MeraLawyer<b>.pk</b></span><span class="logo-tag">Hire a lawyer, the easy way</span></span>
</a>
<nav id="site-nav" class="nav" aria-label="Main">
<div class="nav-dd"><button type="button" aria-expanded="false" aria-haspopup="true">Hire a lawyer {icon('chev', 14, 'currentColor', 2, 'chev')}</button>
<div class="nav-dd-menu">{areas}<a class="all" href="/hire-a-lawyer/">All practice areas</a></div></div>
<div class="nav-dd"><button type="button" aria-expanded="false" aria-haspopup="true">Legal services {icon('chev', 14, 'currentColor', 2)}</button>
<div class="nav-dd-menu">{svcs}<a class="all" href="/legal-services/">All legal services</a></div></div>
<a href="/lawyer-in-islamabad/"{cur('isb')}>Islamabad</a>
<a href="/lawyer-in-rawalpindi/"{cur('rwp')}>Rawalpindi</a>
<div class="nav-dd"><button type="button" aria-expanded="false" aria-haspopup="true">About {icon('chev', 14, 'currentColor', 2)}</button>
<div class="nav-dd-menu"><a href="/about/">About MeraLawyer.pk</a><a href="/about/{CEO['slug']}/">{E(CEO['name'])}, CEO</a></div></div>
<a href="/faq/"{cur('faq')}>FAQ</a>
<a href="/contact/"{cur('contact')}>Contact</a>
<div class="nav-cta">
<a class="btn btn-gold" href="/contact/">Book a consultation</a>
<div class="nav-cta-row">
<a class="btn btn-ghost" href="{TEL}">{icon('phone', 18, 'currentColor', 2)} Call</a>
<a class="btn btn-wa" href="{WA_URL}" target="_blank" rel="noopener">{icon('wa', 18, 'currentColor', 2)} WhatsApp</a>
</div>
<p class="nav-cta-note">{E(C['hours_display'])}</p>
</div>
</nav>
<a class="btn btn-gold header-cta" href="/contact/">Book a consultation</a>
<button class="menu-btn" type="button" aria-controls="site-nav" aria-expanded="false" aria-label="Open menu">{icon('menu', 22, 'currentColor', 2, 'i-open')}{icon('x', 22, 'currentColor', 2, 'i-close')}</button>
</div></header>
"""

def footer():
    areas = "".join(f'<li><a href="/hire-a-lawyer/{a["slug"]}/">{E(a["name"])}</a></li>' for a in AREAS)
    sv = ["company-registration", "income-tax-return", "ntn-registration", "sales-tax-registration", "trademark-registration", "legal-notice", "khula", "succession-certificate"]
    svcs = "".join(f'<li><a href="/legal-services/{s}/">{E(S_BY[s]["name"])}</a></li>' for s in sv)
    return f"""<footer class="site-footer"><div class="wrap">
<div class="foot-grid">
<div>
<div class="logo-name" style="color:#F5F6F2">MeraLawyer<b>.pk</b></div>
<p class="urdu" style="font-size:22px;line-height:2.1;color:{GOLD};margin-top:6px" lang="ur" dir="rtl">میرا وکیل، میرا حق</p>
<p style="margin-top:6px;max-width:34ch">Helping people in Islamabad and Rawalpindi hire lawyers who handle their kind of case, with the fee agreed upfront.</p>
</div>
<div><h2>Hire a lawyer</h2><ul>{areas}<li><a href="/lawyer-in-islamabad/">Lawyer in Islamabad</a></li><li><a href="/lawyer-in-rawalpindi/">Lawyer in Rawalpindi</a></li><li><a href="/about/{CEO['slug']}/">Our CEO</a></li></ul></div>
<div><h2>Legal services</h2><ul>{svcs}<li><a href="/legal-services/">All services</a></li></ul></div>
<div><h2>Contact</h2>
<address>
<span>Islamabad: {E(C['isb_address'])}</span>
<span>Rawalpindi: {E(C['rwp_address'])}</span>
<a href="{TEL}">{E(C['phone_display'])}</a>
<a href="mailto:{E(C['email'])}">{E(C['email'])}</a>
<span>{E(C['hours_display'])}</span>
</address></div>
</div>
<div class="foot-bottom">
<span>© <span id="year">2026</span> {E(C['brand'])}. <a href="/privacy-policy/">Privacy policy</a> · <a href="/disclaimer/">Disclaimer</a> · <a href="/sitemap.xml">Sitemap</a></span>
<span>Information on this site is general and is not legal advice for your situation.</span>
</div>
<p class="powered">Powered by <a href="https://rxdirect.pk/" target="_blank" rel="noopener">RXDirect.pk</a></p>
</div></footer>
<a class="wa-float" href="{WA_URL}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">{icon('wa', 30, '#FFFFFF', 1.8)}</a>
<nav class="tabbar" aria-label="Quick links">
<a href="/" data-tab="/">{icon('home', 22, 'currentColor', 1.9)}<span>Home</span></a>
<a href="/hire-a-lawyer/" data-tab="/hire-a-lawyer/">{icon('gavel', 22, 'currentColor', 1.9)}<span>Lawyers</span></a>
<a class="tab-main" href="{TEL}" aria-label="Call {E(C['phone_display'])}"><span class="tab-main-ic">{icon('phone', 24, 'currentColor', 2)}</span><span>Call</span></a>
<a href="/legal-services/" data-tab="/legal-services/">{icon('doc', 22, 'currentColor', 1.9)}<span>Services</span></a>
<a class="tab-wa" href="{WA_URL}" target="_blank" rel="noopener">{icon('wa', 22, 'currentColor', 1.9)}<span>WhatsApp</span></a>
</nav>
<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""

MATTERS = ["Family matter (khula, divorce, custody)", "Criminal case (bail, FIR, defence)", "Property or civil dispute", "Company registration", "Tax return filing or NTN", "Sales tax or trademark", "Overseas Pakistani matter", "Legal notice or agreement", "Something else"]

def match_form(fid, heading="Get matched with a lawyer", preset=None, city=None, h="h2", details=False):
    opts = "".join(f'<option{" selected" if preset == m else ""}>{E(m)}</option>' for m in MATTERS)
    c1 = "" if city == "Rawalpindi" else " checked"
    c2 = " checked" if city == "Rawalpindi" else ""
    det = f'<div class="field"><label for="{fid}-d">Briefly, what happened? (optional)</label><textarea class="input" id="{fid}-d" name="details"></textarea></div>' if details else ""
    return f"""<div class="match" id="{fid}">
<{h} class="match-title" style="font-family:var(--serif)">{E(heading)}</{h}>
<p class="sub">Free to ask. A case manager replies to understand your matter.</p>
<form class="match-form" data-wa="{C['whatsapp']}" action="{WA_URL}" method="get">
<div class="field"><fieldset><legend>Your city</legend><div class="cities">
<label><input type="radio" name="city" value="Islamabad"{c1}><span>Islamabad</span></label>
<label><input type="radio" name="city" value="Rawalpindi"{c2}><span>Rawalpindi</span></label>
</div></fieldset></div>
<div class="field"><label for="{fid}-m">What do you need help with?</label><select class="input" id="{fid}-m" name="matter">{opts}</select></div>
<div class="field"><label for="{fid}-n">Your name</label><input class="input" id="{fid}-n" name="name" autocomplete="name" required placeholder="Full name"></div>
<div class="field"><label for="{fid}-p">Mobile or WhatsApp number</label><input class="input" id="{fid}-p" name="phone" type="tel" autocomplete="tel" inputmode="tel" required placeholder="03XX XXXXXXX"></div>
{det}
<button class="btn btn-gold" type="submit">{icon('wa', 18, 'currentColor', 1.8)} Send on WhatsApp</button>
<p class="privacy">{icon('lock', 14, 'currentColor', 2)} <span class="form-note" aria-live="polite">Everything you share stays confidential.</span></p>
</form>
</div>"""

def crumbs_html(items):
    lis = "".join(f'<li><a href="{p}">{E(n)}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{E(n)}</li>' for i, (n, p) in enumerate(items))
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{lis}</ol></nav>'

def page_hero(items, h1, lead, urdu="میرا وکیل"):
    return f"""<section class="page-hero">
<div class="watermark" aria-hidden="true">{urdu}</div>
<div class="wrap">
{crumbs_html(items)}
<h1>{E(h1)}</h1>
{f'<p class="lead">{E(lead)}</p>' if lead else ''}
<div class="byline"><span>Reviewed by {E(C['reviewer'])}</span><span>Last updated <time datetime="{C['updated']}">{fmt_date(C['updated'])}</time></span></div>
<div class="hero-actions"><a class="btn btn-gold" href="#match">Get matched with a lawyer</a><a class="btn btn-ghost" href="{WA_URL}" target="_blank" rel="noopener">{icon('wa', 18, 'currentColor', 1.8)} WhatsApp us</a></div>
</div></section>"""

def fmt_date(iso):
    y, m, d = iso.split("-")
    return "%d %s %s" % (int(d), ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][int(m) - 1], y)

def answer_box(label, text):
    return f'<div class="wrap"><div class="answer"><h2>{E(label)}</h2><p>{E(text)}</p></div></div>'

def faq_html(faqs, heading="Frequently asked questions", hid="faq-h"):
    items = "".join(f'<details{" open" if i == 0 else ""}><summary><h3>{E(q)}</h3><span class="plus" aria-hidden="true">{icon("plus", 16, "currentColor", 2)}</span></summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(faqs))
    return f'<h2 id="{hid}">{E(heading)}</h2><div class="faq" style="margin-top:20px">{items}</div>'

def cta():
    return f"""<section class="cta"><div class="watermark" aria-hidden="true">انصاف</div><div class="wrap">
<h2>Talk to a lawyer before the next hearing</h2>
<p>Call, WhatsApp or send your details. Consultations in Urdu or English.</p>
<div class="hero-actions"><a class="btn btn-gold" href="/contact/">Book a consultation</a><a class="btn btn-ghost" href="{TEL}">{icon('phone', 18, 'currentColor', 1.8)} Call {E(C['phone_display'])}</a></div>
</div></section>"""

def svc_card(s, show_cat=False):
    cat = f'<span class="cat-label">{E(s["cat"])}</span>' if show_cat else ""
    return f'<a class="card" href="/legal-services/{s["slug"]}/" data-cat="{slug(s["cat"])}"><span class="ic">{icon(SVC_ICON[s["slug"]], 24, GOLD)}</span>{cat}<h3>{E(s["name"])}</h3><p>{E(s["meta"].split(". ")[0])}.</p><span class="more">Learn more and get started</span></a>'

def area_card(a, dark=True):
    return f'<a class="card{" dark" if dark else ""}" href="/hire-a-lawyer/{a["slug"]}/"><span class="ic">{icon(AREA_ICON[a["slug"]], 24, GOLD)}</span><span class="card-urdu" lang="ur" dir="rtl">{a["urdu"]}</span><h3 style="margin-top:4px">{E(a["name"])}</h3><p>{E(", ".join(c[0] for c in a["cases"][:4]))} and more.</p><span class="more">Hire a {E(a["short"].lower())} lawyer</span></a>'

def ticks(items, one=False):
    return '<ul class="ticks%s">%s</ul>' % (" one" if one else "", "".join(f"<li>{TICK}<span>{x}</span></li>" for x in items))

def write(path, title, desc, body, schema, active="", og_type="website", noindex=False, sitemap=True, priority="0.7"):
    out = os.path.join(OUT, path.strip("/"), "index.html") if path != "/404" else os.path.join(OUT, "404.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc = head(path if path != "/404" else "/404.html", title, desc, schema, og_type, noindex) + header(active) + '<main id="main">' + body + "</main>" + footer()
    open(out, "w", encoding="utf-8").write(doc)
    if sitemap: PAGES.append((path, title, desc, priority))

# ------------------------------------------------------------------ pages
def home():
    t = "Hire a Lawyer in Islamabad & Rawalpindi | MeraLawyer.pk"
    d = "Hire a vetted lawyer in Islamabad and Rawalpindi for family, criminal, property and corporate cases, plus company registration and tax filing. Fee upfront."
    words = ["khula or divorce", "a bail application", "a property dispute", "child custody", "registering a company", "filing your tax return", "a trademark", "property abroad"]
    rot = "".join(f'<span class="{"on" if i == 0 else ""}">{E(w)}</span>' for i, w in enumerate(words))
    marquee = "".join(f'<span>{E(c)}{icon("star", 14, "#0D2B26", 0)}</span>' for c in COURTS * 2).replace('fill="none" stroke="#0D2B26" stroke-width="0"', 'fill="#0D2B26"')
    cats = []
    for s in SERVICES:
        if s["cat"] not in cats: cats.append(s["cat"])
    chips = f'<button class="chip" type="button" data-cat="all" aria-pressed="true">All services <span class="n">{len(SERVICES)}</span></button>' + "".join(
        f'<button class="chip" type="button" data-cat="{slug(c)}" aria-pressed="false">{E(c)} <span class="n">{sum(1 for s in SERVICES if s["cat"] == c)}</span></button>' for c in cats)
    whys = [("shield", "Licensed, vetted advocates", "Every lawyer is enrolled with the bar council and checked before joining."),
            ("rupee", "Fees agreed in advance", "A clear quote before you commit, in writing if you want it."),
            ("wa", "Updates after every hearing", "Know what happened in court and what comes next, on WhatsApp."),
            ("lock", "Complete confidentiality", "Your matter is discussed only with you and your lawyer.")]
    why = "".join(f'<li><span class="ring">{icon(i, 20, GOLD, 1.8)}</span><div><h3>{E(a)}</h3><p>{E(b)}</p></div></li>' for i, a, b in whys)
    steps = [("Tell us what happened", "Call, WhatsApp or fill the form. A case manager listens and asks the right questions."),
             ("Get matched", "We connect you with an advocate who handles this exact kind of case in your city."),
             ("Agree the fee", "You hear the full fee and the plan before anything starts."),
             ("Your lawyer takes over", "Filing, hearings and paperwork are handled, with an update after every hearing.")]
    st = "".join(f"<li><h3>{E(a)}</h3><p>{E(b)}</p></li>" for a, b in steps)
    cities = "".join(f'<a class="card" href="/{c["slug"]}/"><span class="card-urdu" lang="ur" dir="rtl" style="font-size:34px">{c["urdu"]}</span><h3 style="font-family:var(--serif);font-size:32px;font-weight:600">Lawyer in {c["city"]}</h3><p>{E(", ".join(c["courts"][:3]))}.</p><span class="more">See lawyers in {c["city"]}</span></a>' for c in CITIES)
    body = f"""
<section class="hero">
<div class="watermark" aria-hidden="true">میرا وکیل</div>
<div class="wrap hero-grid">
<div>
<p class="pill rise d1">{icon('shield', 16, GOLD, 2)} Licensed advocates in Islamabad and Rawalpindi</p>
<h1 class="rise d2">Hire the right lawyer in Islamabad and Rawalpindi</h1>
<p class="rotator rise d3">Need help with <span class="rot" aria-live="off">{rot}</span></p>
<p class="lead rise d4">Tell us what happened. We match you with a vetted advocate who handles exactly this kind of matter, and you know the fee before you commit. We also handle company registration, tax filing, legal notices and documents.</p>
<div class="hero-actions rise d5"><a class="btn btn-gold" href="#match">Find my lawyer</a><a class="btn btn-ghost" href="{WA_URL}" target="_blank" rel="noopener">{icon('wa', 18, 'currentColor', 1.8)} Chat on WhatsApp</a></div>
</div>
<div class="rise d4">{match_form('match')}</div>
</div></section>
<div class="marquee" aria-label="Courts our lawyers appear in"><div class="marquee-track">{marquee}</div></div>
{answer_box('What is MeraLawyer.pk?', 'MeraLawyer.pk is a legal services platform in Islamabad and Rawalpindi. It matches people with vetted advocates for family, criminal, property, corporate and overseas Pakistani matters, and handles legal services such as SECP company registration, FBR tax return filing, legal notices, court marriage, khula and property transfer, with the fee quoted upfront.')}
<section class="section" aria-labelledby="areas-h"><div class="wrap">
<div class="section-head"><h2 id="areas-h">Hire a lawyer for the matter you are facing</h2><p>Every advocate on MeraLawyer.pk practises in a defined area. Pick yours to see what they handle.</p></div>
<div class="grid-3">{"".join(area_card(a) for a in AREAS)}
<a class="card" href="/contact/"><span class="ic">{icon('chat', 24, GOLD)}</span><h3>Not sure which lawyer you need?</h3><p>Describe your situation and a case manager will point you to the right advocate.</p><span class="more">Ask a case manager</span></a>
</div></div></section>
<section class="section alt" aria-labelledby="svc-h"><div class="wrap">
<div class="section-head"><h2 id="svc-h">Legal services, handled start to finish</h2><p>Not every legal need is a court case. Company registration, tax filing, documents and property work, filed by a lawyer with a fixed fee quoted upfront.</p></div>
<div class="chips" data-filter-group="svc-grid" role="group" aria-label="Filter services">{chips}</div>
<div class="grid-4 svc-grid" id="svc-grid">{"".join(svc_card(s, True) for s in SERVICES)}</div>
<p style="margin-top:36px"><a class="btn btn-ink" href="/legal-services/">See all legal services</a></p>
</div></section>
<section class="section" aria-labelledby="how-h"><div class="wrap">
<h2 id="how-h" style="margin-bottom:56px">How hiring a lawyer works</h2>
<ol class="steps">{st}</ol>
</div></section>
<section style="padding-bottom:110px"><div class="wrap"><div class="panel">
<div><h2>Legal help you can actually follow</h2><p class="lead">Most people dread courts because they never know what is happening with their case. MeraLawyer.pk is built to change that.</p><div class="hero-actions"><a class="btn btn-gold" href="/contact/">Start with a free call</a></div></div>
<ul class="why">{why}</ul>
</div></div></section>
<section class="section alt" aria-labelledby="city-h"><div class="wrap">
<div class="section-head"><h2 id="city-h">Lawyers in the twin cities</h2><p>Islamabad and Rawalpindi follow different provincial rules for land records, sales tax and more. Your lawyer knows the local courts and offices.</p></div>
<div class="grid-2" style="gap:22px">{cities}</div>
</div></section>
<section class="section quote" aria-label="Client testimonial"><div class="wrap">
{icon('chat', 48, '#8A6A1F', 1.4)}
<blockquote>[A short quote from a real client about how their case was handled.]</blockquote>
<p style="margin-top:24px;font-weight:700">[Client name]</p><p class="muted">[Matter type], [Islamabad or Rawalpindi]</p>
</div></section>
<section class="section white"><div class="wrap grid-2" style="align-items:start">
<div><h2>Questions people ask before hiring a lawyer</h2><p class="muted" style="margin-top:18px;max-width:40ch">Still unsure? Send us your question on WhatsApp and a case manager will reply.</p><div class="hero-actions"><a class="btn btn-ink" href="/faq/">Read all FAQs</a></div></div>
<div class="faq">{"".join(f'<details{" open" if i == 0 else ""}><summary><h3>{E(q)}</h3><span class="plus" aria-hidden="true">{icon("plus", 16, "currentColor", 2)}</span></summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(GENERAL_FAQS[:5]))}</div>
</div></section>
{cta()}"""
    write("/", t, d, body, graph("/", t, d, None, "WebPage", faqs=GENERAL_FAQS[:5]), priority="1.0")

def hire_hub():
    path = "/hire-a-lawyer/"; t = "Hire a Lawyer by Practice Area | MeraLawyer.pk"
    d = "Find the right lawyer in Islamabad and Rawalpindi: family, criminal, property, corporate and overseas Pakistani matters. Vetted advocates, fee quoted upfront."
    cr = [("Home", "/"), ("Hire a lawyer", path)]
    blocks = "".join(f"""<section style="margin-top:64px" aria-labelledby="h-{a['slug']}"><h2 id="h-{a['slug']}"><a href="/hire-a-lawyer/{a['slug']}/" style="color:inherit;text-decoration:none">{E(a['name'])}</a></h2><p class="muted" style="margin-top:14px;max-width:70ch">{E(a['answer'])}</p><div style="margin-top:20px">{ticks([c[0] for c in a['cases']])}</div><p style="margin-top:20px"><a class="btn btn-ink" href="/hire-a-lawyer/{a['slug']}/">Hire a {E(a['short'].lower())} lawyer</a></p></section>""" for a in AREAS)
    items = [{"@type": "ItemList", "@id": D + path + "#list", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": a["name"], "url": f"{D}/hire-a-lawyer/{a['slug']}/"} for i, a in enumerate(AREAS)]}]
    body = page_hero(cr, "Hire a lawyer in Islamabad and Rawalpindi", "Choose the area of law that matches your matter. Each page explains what the lawyer does, the cases they handle and common questions.") + \
        answer_box("How do I hire a lawyer in Islamabad or Rawalpindi?", "Identify the area of law your matter falls under, then speak to an advocate who practises in that area in your city. With MeraLawyer.pk you describe your matter once, a case manager matches you with a vetted advocate, and you agree the fee before work starts.") + \
        f'<div class="section"><div class="wrap"><div class="grid-3">{"".join(area_card(a) for a in AREAS)}</div>{blocks}</div></div>' + cta()
    write(path, t, d, body, graph(path, t, d, cr, "CollectionPage", items), priority="0.9")

def area_page(a):
    path = f"/hire-a-lawyer/{a['slug']}/"; cr = [("Home", "/"), ("Hire a lawyer", "/hire-a-lawyer/"), (a["name"], path)]
    cases = "".join(f'<div class="card"><h3 style="margin-top:0">{E(n)}</h3><p>{E(x)}</p></div>' for n, x in a["cases"])
    rel = "".join(svc_card(S_BY[s]) for s in a["services"])
    others = "".join(f'<li><a href="/hire-a-lawyer/{o["slug"]}/">{E(o["name"])}</a></li>' for o in AREAS if o is not a)
    preset = {"family-lawyer": MATTERS[0], "criminal-lawyer": MATTERS[1], "property-lawyer": MATTERS[2], "corporate-lawyer": MATTERS[3], "overseas-pakistani-lawyer": MATTERS[6]}[a["slug"]]
    body = page_hero(cr, a["h1"], None, a["urdu"]) + answer_box(f"What does a {a['name'].lower()} do?", a["answer"]) + f"""
<div class="section"><div class="wrap article">
<div class="prose">
<section aria-labelledby="cases-h"><h2 id="cases-h">Cases our {E(a['short'].lower())} lawyers handle</h2><div class="grid-2" style="gap:16px;margin-top:24px">{cases}</div></section>
<section aria-labelledby="help-h"><h2 id="help-h">How your lawyer helps</h2>{ticks(a['help'], True)}</section>
<section aria-labelledby="courts-h"><h2 id="courts-h">Courts where our lawyers appear</h2><ul class="tags">{"".join(f"<li>{E(c)}</li>" for c in COURTS)}</ul></section>
<section aria-labelledby="rel-h"><h2 id="rel-h">Related legal services</h2><div class="grid-2" style="gap:16px;margin-top:24px">{rel}</div></section>
<section aria-labelledby="faq-h">{faq_html(a['faqs'])}</section>
<section aria-labelledby="loc-h"><h2 id="loc-h">{E(a['name'])} near you</h2><p>We work with {E(a['name'].lower())}s in both cities. See <a href="/lawyer-in-islamabad/">lawyers in Islamabad</a> or <a href="/lawyer-in-rawalpindi/">lawyers in Rawalpindi</a>.</p></section>
</div>
<aside class="aside">{match_form('match', f"Hire a {a['short'].lower()} lawyer", preset)}
<nav class="side-links" aria-label="Other practice areas"><h2>Other practice areas</h2><ul>{others}</ul></nav></aside>
</div></div>{cta()}"""
    svc = [{"@type": "Service", "@id": D + path + "#service", "name": a["name"] + " in Islamabad and Rawalpindi", "serviceType": a["short"],
            "provider": {"@id": D + "/#org"}, "areaServed": [{"@type": "City", "name": "Islamabad"}, {"@type": "City", "name": "Rawalpindi"}], "description": a["answer"]}]
    write(path, a["title"], a["meta"], body, graph(path, a["title"], a["meta"], cr, "WebPage", svc, a["faqs"]), og_type="article", priority="0.9")

def services_hub():
    path = "/legal-services/"; t = "Legal Services in Islamabad & Rawalpindi | MeraLawyer.pk"
    d = "SECP company registration, tax return filing, NTN, sales tax, trademarks, legal notices, court marriage, khula and property transfer in Islamabad and Rawalpindi."
    cr = [("Home", "/"), ("Legal services", path)]
    cats = []
    for s in SERVICES:
        if s["cat"] not in cats: cats.append(s["cat"])
    blocks = "".join(f'<section style="margin-top:72px" aria-labelledby="c-{slug(c)}"><h2 id="c-{slug(c)}">{E(c)}</h2><div class="grid-4" style="margin-top:28px">{"".join(svc_card(s) for s in SERVICES if s["cat"] == c)}</div></section>' for c in cats)
    items = [{"@type": "ItemList", "@id": D + path + "#list", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": s["name"], "url": f"{D}/legal-services/{s['slug']}/"} for i, s in enumerate(SERVICES)]}]
    body = page_hero(cr, "Legal services in Islamabad and Rawalpindi", "Fixed-fee legal work handled by lawyers, from SECP and FBR filings to notices, agreements and family documentation.") + \
        answer_box("Which legal services do you provide?", "MeraLawyer.pk provides business and tax services (company registration, income tax returns, NTN, sales tax, trademarks), documents and notices (legal notices, agreements, power of attorney), family services (court marriage, khula, succession certificates), property services (verification and transfer) and urgent bail applications, all in Islamabad and Rawalpindi.") + \
        f'<div class="section" style="padding-top:40px"><div class="wrap">{blocks}</div></div>' + cta()
    write(path, t, d, body, graph(path, t, d, cr, "CollectionPage", items), priority="0.9")

def service_page(s):
    path = f"/legal-services/{s['slug']}/"; cr = [("Home", "/"), ("Legal services", "/legal-services/"), (s["name"], path)]
    a = A_BY[s["area"]]
    steps = "".join(f"<li><h3>{E(x)}</h3><p>{E(y)}</p></li>" for x, y in s["steps"])
    rel = "".join(svc_card(S_BY[r]) for r in s["related"] if r in S_BY)
    same = "".join(f'<li><a href="/legal-services/{o["slug"]}/">{E(o["name"])}</a></li>' for o in SERVICES if o["cat"] == s["cat"] and o is not s) or "".join(f'<li><a href="/legal-services/{o}/">{E(S_BY[o]["name"])}</a></li>' for o in s["related"])
    preset = {"Business and tax": MATTERS[4] if "tax" in s["slug"] or "ntn" in s["slug"] else (MATTERS[5] if "trademark" in s["slug"] else MATTERS[3]), "Documents and notices": MATTERS[7], "Family": MATTERS[0], "Property": MATTERS[2], "Overseas Pakistanis": MATTERS[6], "Criminal": MATTERS[1]}[s["cat"]]
    body = page_hero(cr, s["h1"], None) + answer_box(f"Quick answer: {s['name'].lower()}", s["answer"]) + f"""
<div class="section"><div class="wrap article">
<div class="prose">
<section aria-labelledby="who-h"><h2 id="who-h">Who needs {E(s['name'].lower())}?</h2><p>{E(s['who'])}</p></section>
<section aria-labelledby="inc-h"><h2 id="inc-h">What our {E(s['name'].lower())} service includes</h2>{ticks([E(x) for x in s['includes']])}</section>
<section aria-labelledby="proc-h"><h2 id="proc-h">{E(s['name'])} process, step by step</h2><ol class="vsteps" style="margin-top:28px">{steps}</ol></section>
<section aria-labelledby="docs-h"><h2 id="docs-h">Documents required</h2>{ticks([E(x) for x in s['docs']], True)}</section>
<section aria-labelledby="fee-h"><h2 id="fee-h">Fee and timeline</h2><div class="fee" style="margin-top:20px"><p style="font-size:22px;font-weight:700">Our fee: from [PRICE]</p><p class="muted" style="margin-top:8px">Government and official fees are charged at actual cost and shown separately. We confirm the exact fee and expected timeline for your case before you start.</p></div></section>
<section aria-labelledby="law-h"><h2 id="law-h">Laws that apply</h2><ul class="laws" style="margin-top:20px">{"".join(f"<li>{E(l)}</li>" for l in s['laws'])}</ul></section>
<section aria-labelledby="faq-h">{faq_html(s['faqs'], f"{s['name']}: frequently asked questions")}</section>
<section aria-labelledby="rel-h"><h2 id="rel-h">Related services</h2><div class="grid-2" style="gap:16px;margin-top:24px">{rel}</div><p style="margin-top:24px">Need representation in court? <a href="/hire-a-lawyer/{a['slug']}/">Hire a {E(a['short'].lower())} lawyer</a>.</p></section>
</div>
<aside class="aside">{match_form('match', f"Get help with {s['name'].lower()}", preset)}
<nav class="side-links" aria-label="More services"><h2>More {E(s['cat'].lower())} services</h2><ul>{same}</ul></nav></aside>
</div></div>{cta()}"""
    svc = [{"@type": "Service", "@id": D + path + "#service", "name": s["name"], "serviceType": s["name"], "category": s["cat"],
            "provider": {"@id": D + "/#org"}, "areaServed": [{"@type": "City", "name": "Islamabad"}, {"@type": "City", "name": "Rawalpindi"}, {"@type": "Country", "name": "Pakistan"}],
            "description": s["answer"], "url": D + path},
           {"@type": "HowTo", "@id": D + path + "#howto", "name": s["h1"], "step": [{"@type": "HowToStep", "position": i + 1, "name": x, "text": y} for i, (x, y) in enumerate(s["steps"])],
            "supply": [{"@type": "HowToSupply", "name": x} for x in s["docs"]]}]
    write(path, s["title"], s["meta"], body, graph(path, s["title"], s["meta"], cr, "WebPage", svc, s["faqs"]), og_type="article", priority="0.8")

def city_page(c):
    path = f"/{c['slug']}/"; cr = [("Home", "/"), (f"Lawyer in {c['city']}", path)]
    other = [x for x in CITIES if x is not c][0]
    top = ["company-registration", "income-tax-return", "khula", "court-marriage", "property-verification", "bail-application", "succession-certificate", "legal-notice"]
    body = page_hero(cr, c["h1"], None, c["urdu"]) + answer_box(f"How do I find a good lawyer in {c['city']}?", c["answer"]) + f"""
<div class="section"><div class="wrap article">
<div class="prose">
<section aria-labelledby="ar-h"><h2 id="ar-h">Lawyers in {c['city']} by practice area</h2><div class="grid-2" style="gap:16px;margin-top:24px">{"".join(area_card(a, False) for a in AREAS)}</div></section>
<section aria-labelledby="ct-h"><h2 id="ct-h">Courts in {c['city']} where our lawyers appear</h2><ul class="tags" style="margin-top:20px">{"".join(f"<li>{E(x)}</li>" for x in c['courts'])}</ul></section>
<section aria-labelledby="sv-h"><h2 id="sv-h">Popular legal services in {c['city']}</h2><div class="grid-2" style="gap:16px;margin-top:24px">{"".join(svc_card(S_BY[s]) for s in top)}</div></section>
<section aria-labelledby="loc-h"><h2 id="loc-h">Areas of {c['city']} we serve</h2><ul class="tags" style="margin-top:20px">{"".join(f"<li>{E(x)}</li>" for x in c['areas'])}</ul><p style="margin-top:20px">Also in the twin city: <a href="/{other['slug']}/">lawyer in {other['city']}</a>.</p></section>
<section aria-labelledby="faq-h">{faq_html(c['faqs'], f"Hiring a lawyer in {c['city']}: questions")}</section>
</div>
<aside class="aside">{match_form('match', f"Get a lawyer in {c['city']}", None, c['city'])}
<div class="side-links"><h2>Office in {c['city']}</h2><p style="margin-top:10px;font-size:15px">{E(C['isb_address'] if c['city'] == 'Islamabad' else C['rwp_address'])}<br><a href="{TEL}">{E(C['phone_display'])}</a><br>{E(C['hours_display'])}</p></div></aside>
</div></div>{cta()}"""
    ex = [{"@type": "Place", "@id": D + path + "#place", "name": c["city"], "geo": {"@type": "GeoCoordinates", "latitude": float(c["lat"]), "longitude": float(c["lng"])},
           "containedInPlace": {"@type": "AdministrativeArea", "name": c["region"]}}]
    write(path, c["title"], c["meta"], body, graph(path, c["title"], c["meta"], cr, "WebPage", ex, c["faqs"]), active="isb" if c["city"] == "Islamabad" else "rwp", priority="0.9")

def about():
    path = "/about/"; t = "About MeraLawyer.pk | Legal Services in Islamabad & Rawalpindi"
    d = "About MeraLawyer.pk: how we vet lawyers, how we set fees, and why we built a simpler way to hire a lawyer in Islamabad and Rawalpindi."
    cr = [("Home", "/"), ("About", path)]
    body = page_hero(cr, "About MeraLawyer.pk", "A simpler, more transparent way to hire a lawyer in the twin cities.") + answer_box("Who is behind MeraLawyer.pk?", "MeraLawyer.pk was founded in [YEAR] by [FOUNDER NAME AND QUALIFICATIONS] to make hiring a lawyer in Islamabad and Rawalpindi simple and transparent. It works with licensed advocates across family, criminal, property and corporate law.") + f"""
<div class="section"><div class="wrap article"><div class="prose">
<section><h2>Why we started</h2><p>[Your story: why you started MeraLawyer.pk and the problem you saw people facing when they needed a lawyer.]</p></section>
<section><h2>How we choose lawyers</h2>{ticks(["Every advocate is enrolled with the relevant bar council, and we check the licence.", "Each lawyer works in defined practice areas, so you are matched to someone who handles your type of case.", "We review client feedback after every matter.", "Lawyers agree to give fee quotes upfront and update clients after hearings."], True)}</section>
<section><h2>Leadership</h2><a class="card" href="/about/{CEO['slug']}/" style="margin-top:20px;flex-direction:row;gap:20px;align-items:center"><span class="ic" style="width:72px;height:72px;border-radius:50%;font-family:var(--serif);color:{GOLD};font-size:26px">{''.join(w[0] for w in CEO['name'].split()[1:])}</span><span><h3 style="margin-top:0">{E(CEO['name'])}</h3><p style="margin-top:4px">{E(CEO['role'])}, {E(C['brand'])}</p><span class="more" style="padding-top:8px;display:block">Read profile</span></span></a></section>
<section><h2>Our lawyers</h2><p>[Add a short profile for each lead lawyer: name, bar enrolment (e.g. Advocate High Court), years of practice, practice areas and courts. Real named experts strengthen trust with clients, search engines and AI assistants.]</p></section>
<section><h2>Our commitments</h2>{ticks(["The fee is agreed before work starts.", "Your information stays confidential.", "You get an update after every hearing.", "Consultations in Urdu or English."], True)}</section>
</div><aside class="aside">{match_form('match')}</aside></div></div>{cta()}"""
    write(path, t, d, body, graph(path, t, d, cr, "AboutPage"), active="about", priority="0.6")

def ceo_page():
    p = CEO; path = f"/about/{p['slug']}/"; url = D + path
    t = f"{p['name']} | {p['role']}, MeraLawyer.pk"
    d = f"{p['name']} is the {p['role'].lower()} of MeraLawyer.pk, helping people in Islamabad and Rawalpindi hire vetted lawyers with fees agreed upfront."
    cr = [("Home", "/"), ("About", "/about/"), (p["name"], path)]
    same = [u for u in (p["instagram"], p["linkedin"], p["facebook"], p["x"]) if u]
    initials = "".join(w[0] for w in p["name"].split()[1:])
    photo = (f'<img src="{E(p["photo"])}" alt="{E(p["name"])}, {E(p["role"])} of MeraLawyer.pk" width="320" height="320" style="width:100%;height:100%;object-fit:cover;border-radius:50%">'
             if p["photo"] else f'<span style="font-family:var(--serif);font-size:96px;font-weight:600;color:{GOLD}">{initials}</span>')
    socials = "".join(f'<a class="btn btn-ghost" href="{E(u)}" target="_blank" rel="noopener me">{n}</a>' for n, u in (("Instagram", p["instagram"]), ("LinkedIn", p["linkedin"]), ("Facebook", p["facebook"]), ("X", p["x"])) if u)
    person = {"@type": "Person", "@id": url + "#person", "name": p["name"], "alternateName": p["urdu"], "jobTitle": p["role"],
              "description": p["summary"], "url": url, "worksFor": {"@id": D + "/#org"},
              "knowsAbout": ["Legal services in Pakistan", "Legal technology", "Company registration", "Tax filing"],
              "address": {"@type": "PostalAddress", "addressLocality": "Islamabad", "addressCountry": "PK"}}
    if p["photo"]: person["image"] = D + p["photo"]
    if same: person["sameAs"] = same
    if p["email"]: person["email"] = p["email"]
    prof = {"@type": "ProfilePage", "@id": url + "#profile", "url": url, "name": t, "mainEntity": {"@id": url + "#person"},
            "dateModified": C["updated"], "isPartOf": {"@id": D + "/#website"}}
    body = f"""<section class="page-hero"><div class="watermark" aria-hidden="true">{p['urdu']}</div><div class="wrap">
{crumbs_html(cr)}
<div class="grid-2" style="align-items:center;margin-top:28px;grid-template-columns:minmax(0,320px) minmax(0,1fr)">
<div class="rise d1" style="width:min(320px,70vw);aspect-ratio:1;border-radius:50%;border:2px solid {GOLD};padding:10px"><div style="width:100%;height:100%;border-radius:50%;background:var(--ink-2);display:flex;align-items:center;justify-content:center;overflow:hidden">{photo}</div></div>
<div>
<p class="pill rise d2">{icon('shield', 16, GOLD, 2)} {E(p['role'])}, {E(C['brand'])}</p>
<h1 class="rise d3" style="margin-top:22px">{E(p['name'])}</h1>
<p class="urdu rise d3" lang="ur" dir="rtl" style="font-size:30px;line-height:2.1;color:{GOLD};text-align:left">{p['urdu']}</p>
<div class="hero-actions rise d4"><a class="btn btn-gold" href="{TEL}">{icon('phone', 18, 'currentColor', 1.8)} Call {E(C['phone_display'])}</a><a class="btn btn-ghost" href="{WA_URL}" target="_blank" rel="noopener">{icon('wa', 18, 'currentColor', 1.8)} WhatsApp</a>{socials}</div>
</div></div></div></section>
{answer_box(f"Who is {p['name']}?", p['summary'])}
<div class="section"><div class="wrap article"><div class="prose">
<section><h2>Why he founded MeraLawyer.pk</h2><p>{E(p['story'])}</p></section>
<section><h2>Background</h2>{ticks([E(x) for x in p['background']], True)}</section>
<section><h2>What he is building</h2>{ticks([E(x) for x in p['focus']], True)}</section>
<section class="quote" style="text-align:left"><blockquote style="margin:0;max-width:30ch">{E(p['quote'])}</blockquote><p style="margin-top:16px;font-weight:700">{E(p['name'])}</p><p class="muted">{E(p['role'])}</p></section>
<section><h2>Contact {E(p['name'].split()[1])}'s office</h2><p>For media, partnerships or to speak to the leadership team, call <a href="{TEL}">{E(C['phone_display'])}</a>, message us on <a href="{WA_URL}" target="_blank" rel="noopener">WhatsApp</a> or email <a href="mailto:{E(p['email'] or C['email'])}">{E(p['email'] or C['email'])}</a>.</p></section>
</div><aside class="aside">{match_form('match')}</aside></div></div>{cta()}"""
    write(path, t, d, body, graph(path, t, d, cr, "WebPage", [person, prof]), active="about", og_type="profile", priority="0.6")

def contact():
    path = "/contact/"; t = "Contact MeraLawyer.pk | Book a Lawyer Consultation"
    d = f"Contact MeraLawyer.pk to book a lawyer consultation in Islamabad or Rawalpindi. Call {C['phone_display']}, WhatsApp us, or send your details online."
    cr = [("Home", "/"), ("Contact", path)]
    maps = lambda q: "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q)
    body = page_hero(cr, "Book a consultation", "Tell us about your matter and a case manager will get back to you.") + f"""
<div class="section"><div class="wrap grid-2" style="align-items:start">
<div>{match_form('match', 'Send us your details', details=True)}</div>
<div class="prose">
<h2>Talk to us directly</h2>
<div style="display:flex;flex-direction:column;gap:14px;margin-top:24px">
<a class="btn btn-ink" href="{TEL}" style="justify-content:flex-start">{icon('phone', 18, 'currentColor', 1.8)} Call {E(C['phone_display'])}</a>
<a class="btn btn-ink" href="{WA_URL}" target="_blank" rel="noopener" style="justify-content:flex-start">{icon('wa', 18, 'currentColor', 1.8)} WhatsApp us</a>
<a class="btn btn-ink" href="mailto:{E(C['email'])}" style="justify-content:flex-start">{icon('mail', 18, 'currentColor', 1.8)} {E(C['email'])}</a>
</div>
<h2 style="margin-top:56px">Offices</h2>
<div class="grid-2" style="gap:16px;margin-top:24px">
<div class="card"><h3 style="margin-top:0">Islamabad</h3><p>{E(C['isb_address'])}</p><a class="more" href="{maps(C['isb_address'])}" target="_blank" rel="noopener">Open in Google Maps</a></div>
<div class="card"><h3 style="margin-top:0">Rawalpindi</h3><p>{E(C['rwp_address'])}</p><a class="more" href="{maps(C['rwp_address'])}" target="_blank" rel="noopener">Open in Google Maps</a></div>
</div>
<p class="muted" style="margin-top:24px">Office hours: {E(C['hours_display'])}. Urgent bail matters: call or WhatsApp any time.</p>
</div></div></div>"""
    write(path, t, d, body, graph(path, t, d, cr, "ContactPage"), active="contact", priority="0.7")

def faq_page():
    path = "/faq/"; t = "Lawyer FAQ: Fees, Courts, Khula, Tax | MeraLawyer.pk"
    d = "Answers to common questions about hiring a lawyer in Islamabad and Rawalpindi: fees, courts, khula, bail, company registration, tax returns and more."
    cr = [("Home", "/"), ("FAQ", path)]
    groups = [("Hiring a lawyer", GENERAL_FAQS)] + [(a["name"], a["faqs"]) for a in AREAS] + [(s["name"], s["faqs"][:2]) for s in SERVICES]
    allf = []; secs = ""
    for i, (g, fs) in enumerate(groups):
        allf += fs
        secs += f'<section style="margin-top:56px" aria-labelledby="fq{i}">{faq_html(fs, g, "fq%d" % i)}</section>'
    body = page_hero(cr, "Frequently asked questions", "Plain answers about lawyers, courts and legal procedures in Islamabad and Rawalpindi.") + \
        f'<div class="section" style="padding-top:40px"><div class="wrap article"><div class="prose">{secs}</div><aside class="aside">{match_form("match", "Still have a question?")}</aside></div></div>' + cta()
    write(path, t, d, body, graph(path, t, d, cr, "WebPage", faqs=allf), active="faq", priority="0.7")

def legal(path, h1, t, d, paras):
    cr = [("Home", "/"), (h1, path)]
    body = page_hero(cr, h1, None) + '<div class="section"><div class="wrap prose">' + "".join(f"<section style='margin-top:40px'><h2 style='font-size:28px'>{E(h)}</h2><p style='margin-top:12px'>{E(p)}</p></section>" for h, p in paras) + "</div></div>"
    write(path, t, d, body, graph(path, t, d, cr), priority="0.3")

def not_found():
    t = "Page not found | MeraLawyer.pk"; d = "The page you were looking for could not be found. Browse legal services or contact MeraLawyer.pk for help with your matter."
    body = f'<section class="page-hero" style="padding:120px 0"><div class="watermark" aria-hidden="true">میرا وکیل</div><div class="wrap"><h1>This page could not be found</h1><p class="lead">The link may be old or mistyped. Try one of these instead.</p><div class="hero-actions"><a class="btn btn-gold" href="/">Go to the home page</a><a class="btn btn-ghost" href="/legal-services/">See legal services</a><a class="btn btn-ghost" href="/contact/">Contact us</a></div></div></section>'
    write("/404", t, d, body, graph("/404.html", t, d, None), noindex=True, sitemap=False)

# ------------------------------------------------------------------ machine-readable files
def extras():
    # sitemap
    urls = "".join(f"<url><loc>{D}{p}</loc><lastmod>{C['updated']}</lastmod><changefreq>monthly</changefreq><priority>{pr}</priority></url>\n" for p, _, _, pr in PAGES)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    # robots: welcome search engines and AI answer engines
    bots = ["Googlebot", "Bingbot", "Google-Extended", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Applebot", "Applebot-Extended", "Amazonbot", "DuckAssistBot", "meta-externalagent", "CCBot", "YandexBot"]
    rb = "# MeraLawyer.pk robots.txt\n# Search engines and AI assistants are welcome to read and cite this site.\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + \
         "User-agent: *\nAllow: /\nDisallow: /404.html\n\n" + f"Sitemap: {D}/sitemap.xml\n# LLM summary: {D}/llms.txt\n"
    open(os.path.join(OUT, "robots.txt"), "w").write(rb)
    # llms.txt (llmstxt.org format)
    L = [f"# {C['brand']}", "", "> MeraLawyer.pk is a legal services platform in Islamabad and Rawalpindi, Pakistan. It matches people with vetted, licensed advocates for family, criminal, property, corporate and overseas Pakistani matters, and provides legal services such as SECP company registration, FBR income tax return filing, NTN and sales tax registration, trademark registration, legal notices, court marriage, khula, succession certificates and property transfer. Fees are quoted upfront. Consultations in Urdu and English.", "",
         f"- Phone: {C['phone']}", f"- WhatsApp: {WA_URL}", f"- Email: {C['email']}", f"- Islamabad office: {C['isb_address']}", f"- Rawalpindi office: {C['rwp_address']}", f"- Hours: {C['hours_display']}", "- Service area: Islamabad Capital Territory and Rawalpindi (Punjab); overseas Pakistanis worldwide", "",
         "## Hire a lawyer", ""] + [f"- [{a['name']}]({D}/hire-a-lawyer/{a['slug']}/): {a['meta']}" for a in AREAS] + \
        ["", "## Legal services", ""] + [f"- [{s['name']}]({D}/legal-services/{s['slug']}/): {s['meta']}" for s in SERVICES] + \
        ["", "## Locations", ""] + [f"- [Lawyer in {c['city']}]({D}/{c['slug']}/): {c['meta']}" for c in CITIES] + \
        ["", "## Optional", "", f"- [FAQ]({D}/faq/): Answers about fees, courts and procedures", f"- [About]({D}/about/)", f"- [{CEO['name']}, {CEO['role']}]({D}/about/{CEO['slug']}/)", f"- [Contact]({D}/contact/)", f"- [Full content for LLMs]({D}/llms-full.txt)", ""]
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write("\n".join(L))
    # llms-full.txt: all key facts in plain markdown
    F = [f"# {C['brand']} — full content", "", L[2], ""]
    for a in AREAS:
        F += [f"## {a['h1']}", f"URL: {D}/hire-a-lawyer/{a['slug']}/", "", a["answer"], "", "Cases handled:"] + [f"- {n}: {x}" for n, x in a["cases"]] + [""] + sum([[f"Q: {q}", f"A: {x}", ""] for q, x in a["faqs"]], [])
    for s in SERVICES:
        F += [f"## {s['h1']}", f"URL: {D}/legal-services/{s['slug']}/", "", s["answer"], "", "Process:"] + [f"{i+1}. {x}: {y}" for i, (x, y) in enumerate(s["steps"])] + ["", "Documents required:"] + [f"- {x}" for x in s["docs"]] + ["", "Laws: " + "; ".join(s["laws"]), ""] + sum([[f"Q: {q}", f"A: {x}", ""] for q, x in s["faqs"]], [])
    for c in CITIES:
        F += [f"## {c['h1']}", f"URL: {D}/{c['slug']}/", "", c["answer"], "", "Courts: " + "; ".join(c["courts"]), "Areas served: " + ", ".join(c["areas"]), ""]
    F += ["## General questions", ""] + sum([[f"Q: {q}", f"A: {x}", ""] for q, x in GENERAL_FAQS], [])
    open(os.path.join(OUT, "llms-full.txt"), "w", encoding="utf-8").write("\n".join(F))
    # manifest
    json.dump({"name": C["brand"], "short_name": "MeraLawyer", "start_url": "/", "display": "standalone", "background_color": "#0D2B26", "theme_color": "#0D2B26",
               "icons": [{"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]},
              open(os.path.join(OUT, "site.webmanifest"), "w"), indent=1)
    # favicon
    fav = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0D2B26"/><g transform="translate(12 12) scale(1.67)" fill="none" stroke="{GOLD}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + "".join(f'<path d="{("M"+p) if not p.startswith("M") else p}"/>' for p in P["scale"].split(" M")) + "</g></svg>"
    open(os.path.join(OUT, "favicon.svg"), "w").write(fav)

def images():
    from PIL import Image, ImageDraw, ImageFont
    img_dir = os.path.join(OUT, "assets", "img"); os.makedirs(img_dir, exist_ok=True)
    ink, gold, paper = (13, 43, 38), (200, 162, 74), (245, 246, 242)
    serif = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"; sans = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    def scale_icon(d, cx, cy, s, w):
        # draw the scales mark (stroke) at centre cx,cy with unit s
        L = lambda pts: d.line([(cx + (x - 12) * s, cy + (y - 12) * s) for x, y in pts], fill=gold, width=w, joint="curve")
        L([(12, 3), (12, 21)]); L([(7, 21), (17, 21)]); L([(4, 7), (20, 7)])
        L([(4, 7), (1.5, 13), (6.5, 13), (4, 7)]); L([(20, 7), (17.5, 13), (22.5, 13), (20, 7)])
    og = Image.new("RGB", (1200, 630), ink); d = ImageDraw.Draw(og)
    for x in range(0, 1200, 28):
        for y in range(0, 630, 28): d.point((x, y), fill=(30, 62, 56))
    d.ellipse((80, 80, 180, 180), outline=gold, width=4); scale_icon(d, 130, 130, 3.2, 4)
    d.text((80, 230), "MeraLawyer.pk", font=ImageFont.truetype(serif, 92), fill=paper)
    d.text((80, 350), "Hire the right lawyer in", font=ImageFont.truetype(serif, 48), fill=paper)
    d.text((80, 410), "Islamabad and Rawalpindi", font=ImageFont.truetype(serif, 48), fill=gold)
    d.text((80, 520), "Family · Criminal · Property · Company registration · Tax filing", font=ImageFont.truetype(sans, 26), fill=(201, 211, 205))
    og.save(os.path.join(img_dir, "og-image.png"), optimize=True)
    for size, name in [(180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png"), (512, "logo.png")]:
        im = Image.new("RGB", (size, size), ink); dd = ImageDraw.Draw(im)
        scale_icon(dd, size / 2, size / 2, size / 36, max(2, size // 40)); im.save(os.path.join(img_dir, name))
    ico = Image.new("RGB", (64, 64), ink); scale_icon(ImageDraw.Draw(ico), 32, 32, 1.8, 3); ico.save(os.path.join(OUT, "favicon.ico"), sizes=[(32, 32)])

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    shutil.copytree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"), OUT)
    home(); hire_hub(); services_hub(); about(); ceo_page(); contact(); faq_page()
    for a in AREAS: area_page(a)
    for s in SERVICES: service_page(s)
    for c in CITIES: city_page(c)
    legal("/privacy-policy/", "Privacy policy", "Privacy Policy | MeraLawyer.pk", "How MeraLawyer.pk collects, uses and protects the information you share when you contact us about a legal matter.", [
        ("What we collect", "The name, phone number, city and description of your matter that you send us by form, phone, email or WhatsApp."),
        ("How we use it", "Only to understand your matter, match you with a lawyer and contact you about it. We do not sell your information."),
        ("Who sees it", "Our case managers and the lawyer you are matched with. Lawyers are bound by professional confidentiality."),
        ("Your choices", f"You can ask us to delete your information at any time by writing to {C['email']}."),
        ("Updates", "[Have a lawyer review this policy before publishing, and add your full policy text here.]")])
    legal("/disclaimer/", "Disclaimer", "Legal Disclaimer | MeraLawyer.pk", "Important information about the general legal content on MeraLawyer.pk. It is not legal advice for your specific situation.", [
        ("General information only", "Content on this website explains Pakistani law and procedures in general terms. It is not legal advice for your situation and does not create a lawyer-client relationship."),
        ("Laws change", "Laws, fees and official procedures change. Always confirm the current position with a lawyer before acting."),
        ("No guaranteed outcome", "No lawyer can guarantee the result of a case. Outcomes depend on facts, evidence and the court.")])
    not_found(); extras(); images()
    print(f"Built {len(PAGES) + 1} pages into {OUT}")

if __name__ == "__main__":
    build()
