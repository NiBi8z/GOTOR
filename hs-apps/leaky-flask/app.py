#!/usr/bin/env python3

import requests
from flask import (Flask, Response, abort, redirect, render_template_string,
                   request, url_for)

app = Flask(__name__)

IMAGE_CACHE = {}
USER_LISTINGS = []
_next_id = [100]


def fetch_product_photo(url):
    """Télécharge la photo CÔTÉ SERVEUR avant publication ("mise en cache CDN").

    C'EST LA FAILLE : aucune validation de l'URL (SSRF), et la requête part en
    DIRECT (pas de proxy Tor) -> l'hôte visé voit l'IP réelle du serveur.
    """
    r = requests.get(url, timeout=5, allow_redirects=True)
    ctype = r.headers.get("Content-Type", "application/octet-stream")
    return ctype, r.content[:262144], r.status_code


SEED = [
    {"id": 1, "cat": "0day",     "title": "Full RCE chain — unauth, pre-patch",
     "vendor": "darksmith",  "rating": 4.9, "reviews": 212, "btc": "0.84", "xmr": "7.1",
     "src": "WW", "dst": "WW", "fe": False},
    {"id": 2, "cat": "Cards",    "title": "CC dump pack ×500 — US, 90%+ valid",
     "vendor": "plastic_king","rating": 4.6, "reviews": 1480, "btc": "0.031", "xmr": "0.26",
     "src": "US", "dst": "WW", "fe": True},
    {"id": 3, "cat": "Accounts", "title": "Aged verified payment accounts (×10)",
     "vendor": "acct_forge", "rating": 4.3, "reviews": 377, "btc": "0.045", "xmr": "0.38",
     "src": "EU", "dst": "WW", "fe": False},
    {"id": 4, "cat": "Services", "title": "Stress service — 100 Gbps / 1h slot",
     "vendor": "stormcloud", "rating": 4.1, "reviews": 903, "btc": "0.012", "xmr": "0.10",
     "src": "WW", "dst": "WW", "fe": True},
    {"id": 5, "cat": "Docs",     "title": "KYC bypass bundle — templates + guide",
     "vendor": "ghostdocs",  "rating": 4.7, "reviews": 256, "btc": "0.067", "xmr": "0.56",
     "src": "WW", "dst": "WW", "fe": False},
    {"id": 6, "cat": "Malware",  "title": "Loader + panel — monthly lease",
     "vendor": "cryptolock", "rating": 4.8, "reviews": 141, "btc": "0.15", "xmr": "1.26",
     "src": "RU", "dst": "WW", "fe": False},
]
CATEGORIES = ["0day", "Cards", "Accounts", "Services", "Docs", "Malware", "Leaks", "Phishing"]


def all_listings():
    return USER_LISTINGS + SEED


def _cat_counts():
    c = {k: 0 for k in CATEGORIES}
    for l in all_listings():
        c[l["cat"]] = c.get(l["cat"], 0) + 1
    return c


SHELL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} · Nightbazaar</title>
<style>
:root{--bg:#0a0c0f;--panel:#111519;--panel2:#161b21;--line:#232b33;--txt:#c7cfc9;
--mut:#6e7c73;--mut2:#4a564e;--grn:#79c46b;--grn2:#3f7a37;--gold:#d7a63f;--red:#df6a3c}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);
font-family:ui-sans-serif,system-ui,"Segoe UI",Roboto,sans-serif;font-size:14px;line-height:1.5}
a{color:var(--grn);text-decoration:none}a:hover{text-decoration:underline}
code,.mono{font-family:ui-monospace,"JetBrains Mono",Menlo,Consolas,monospace}
.bar{display:flex;align-items:center;gap:18px;padding:9px 18px;background:#0c0f13;
border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.brand{font-weight:800;letter-spacing:.5px;font-size:16px;color:#e7efe7}
.brand b{color:var(--grn)}
.nav{display:flex;gap:16px;font-size:13px}
.nav a{color:var(--mut)}.nav a:hover{color:var(--txt)}
.sell-link{color:var(--grn)!important}
.right{margin-left:auto;display:flex;gap:16px;align-items:center;font-size:12.5px}
.bal{font-family:ui-monospace,monospace;color:var(--gold)}
.warn{background:#1c130c;border-bottom:1px solid #3a2414;color:#e8b088;
padding:7px 18px;font-size:12.5px}
.warn b{color:var(--red)}
.layout{display:grid;grid-template-columns:200px 1fr;gap:0;min-height:calc(100vh - 120px)}
.side{border-right:1px solid var(--line);padding:16px 0}
.side h4{margin:0 16px 8px;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:var(--mut2)}
.side a{display:flex;justify-content:space-between;padding:6px 16px;color:var(--mut);font-size:13px}
.side a:hover{background:var(--panel);color:var(--txt);text-decoration:none}
.side a .n{color:var(--mut2);font-family:ui-monospace,monospace}
.main{padding:18px 22px}
.listings{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px}
.card{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);
border-radius:8px;padding:13px 14px;display:flex;flex-direction:column;gap:7px;transition:border-color .15s}
.card:hover{border-color:#36414a}
.thumb{width:100%;height:120px;object-fit:cover;border-radius:6px;border:1px solid var(--line);background:#0c0f13}
.tag{align-self:flex-start;font-size:10.5px;letter-spacing:.6px;text-transform:uppercase;
color:var(--grn);border:1px solid var(--grn2);border-radius:999px;padding:1px 8px}
.card h3{margin:0;font-size:14px;font-weight:650;line-height:1.35}
.card h3 a{color:var(--txt)}
.meta{display:flex;justify-content:space-between;font-size:12px;color:var(--mut);margin-top:auto}
.vend{color:var(--mut)}.vend b{color:#9fb4a4;font-weight:600}
.stars{color:var(--gold)}
.price{font-family:ui-monospace,monospace;color:var(--gold);font-size:13px}
.ship{font-size:11.5px;color:var(--mut2);font-family:ui-monospace,monospace}
.fe{color:var(--red);font-size:10.5px;border:1px solid #4a2a1c;border-radius:4px;padding:0 5px}
.status{display:flex;gap:22px;flex-wrap:wrap;padding:9px 18px;border-top:1px solid var(--line);
background:#0c0f13;color:var(--mut2);font-size:11.5px;font-family:ui-monospace,monospace}
.status b{color:var(--mut)}
.prod{max-width:720px}
.prod .tag{margin-bottom:10px}
.prod h1{font-size:20px;margin:0 0 6px}
.prod .sub{color:var(--mut);margin-bottom:16px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px 18px;margin:14px 0}
.row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--line);font-size:13px}
.row:last-child{border:0}.row .k{color:var(--mut)}
.buy{display:inline-block;margin-top:8px;background:var(--grn2);color:#eaf6e8;border:0;
padding:10px 20px;border-radius:7px;font-weight:650;cursor:pointer;font-size:14px}
.buy:hover{background:var(--grn);text-decoration:none}
.muted{color:var(--mut)}
form.sell label{display:flex;flex-direction:column;gap:5px;font-size:12.5px;color:var(--mut)}
form.sell input,form.sell select{background:var(--bg);border:1px solid var(--line);color:var(--txt);
font-size:13.5px;padding:9px 11px;border-radius:7px;outline:none;font-family:inherit}
form.sell input:focus,form.sell select:focus{border-color:var(--grn2)}
.hint{font-size:11.5px;color:var(--mut2);font-family:ui-monospace,monospace}
.prodimg{max-width:340px;border:1px solid var(--line);border-radius:8px;margin-bottom:12px}
</style></head>
<body>
<div class="bar">
  <div class="brand">NIGHT<b>BAZAAR</b></div>
  <div class="nav">
    <a href="/">Market</a>
    <a href="/sell" class="sell-link">+ Sell an item</a>
    <a href="/wallet">Wallet</a>
    <a href="/">Messages (0)</a>
  </div>
  <div class="right">
    <span class="bal">▲ 0.0431 BTC</span>
    <span class="muted">user: <b>guest</b></span>
    <a href="/">PGP</a><a href="/">Logout</a>
  </div>
</div>
<div class="warn">⚠ <b>PHISHING WARNING</b> — only trust PGP-signed mirror links. Never enter your
mnemonic. This market uses <b>escrow</b> &amp; <b>2-FA</b>. Current canary signed 2026-10-20.</div>
<div class="layout">
  <aside class="side">
    <h4>Categories</h4>
    {% for c in categories %}<a href="/">{{ c }} <span class="n">{{ counts[c] }}</span></a>{% endfor %}
    <h4 style="margin-top:18px">Account</h4>
    <a href="/sell">Sell an item <span class="n">+</span></a>
    <a href="/wallet">Wallet <span class="n">↗</span></a>
  </aside>
  <main class="main">{{ content|safe }}</main>
</div>
<div class="status">
  <span><b>mirror:</b> {{ mirror }}</span>
  <span><b>uptime:</b> 41d 06h</span>
  <span><b>vendors:</b> 318</span>
  <span><b>listings:</b> {{ counts.values()|sum }}</span>
  <span><b>XMR/BTC:</b> 0.00841</span>
  <span class="muted">v2.4.0 · onion-only</span>
</div>
</body></html>"""

INDEX_INNER = """
<div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:12px">
  <h2 style="margin:0;font-size:16px">Fresh listings</h2>
  <a class="buy" href="/sell" style="margin:0;padding:7px 14px;font-size:13px">+ Sell an item</a>
</div>
<div class="listings">
{% for l in listings %}
  <div class="card">
    {% if l.has_img %}<a href="/listing/{{ l.id }}"><img class="thumb" src="/img/{{ l.id }}" alt=""></a>{% endif %}
    <span class="tag">{{ l.cat }}</span>
    <h3><a href="/listing/{{ l.id }}">{{ l.title }}</a></h3>
    <div class="meta">
      <span class="vend">by <b>{{ l.vendor }}</b></span>
      <span class="stars">★ {{ "%.1f"|format(l.rating) }} <span class="muted">({{ l.reviews }})</span></span>
    </div>
    <div class="meta">
      <span class="price">₿ {{ l.btc }}</span>
      <span class="ship">{{ l.src }} → {{ l.dst }}{% if l.fe %} · <span class="fe">FE</span>{% endif %}</span>
    </div>
  </div>
{% endfor %}
</div>"""

PRODUCT_INNER = """
<div class="prod">
  <span class="tag">{{ l.cat }}</span>
  <h1>{{ l.title }}</h1>
  <div class="sub">by <b style="color:#9fb4a4">{{ l.vendor }}</b> · <span class="stars">★ {{ "%.1f"|format(l.rating) }}</span>
    <span class="muted">({{ l.reviews }} reviews)</span></div>
  {% if l.has_img %}<img class="prodimg" src="/img/{{ l.id }}" alt="product photo">{% endif %}
  {% if l.note %}<div class="hint">CDN: {{ l.note }}</div>{% endif %}
  <div class="panel">
    <div class="row"><span class="k">Price</span><span class="price">₿ {{ l.btc }} <span class="muted">/ {{ l.xmr }} XMR</span></span></div>
    <div class="row"><span class="k">Ships from → to</span><span class="mono">{{ l.src }} → {{ l.dst }}</span></div>
    <div class="row"><span class="k">Payment</span><span>Escrow{% if l.fe %} · Finalize Early allowed{% endif %}</span></div>
    <div class="row"><span class="k">Stock</span><span>in stock</span></div>
  </div>
  <p class="muted">Auto-dispatch after escrow release. Disputes handled by staff within 72h.
  Encrypt your drop info with the vendor's PGP key before ordering.</p>
  <a class="buy" href="/wallet">Buy with escrow →</a>
</div>"""

SELL_INNER = """
<div class="prod">
  <h1>Create a listing</h1>
  <div class="sub">Your item goes live instantly. Add a product photo by URL —
    we fetch &amp; cache it on our CDN for fast mirror loading.</div>
  {% if error %}<div class="hint" style="color:var(--red)">{{ error }}</div>{% endif %}
  <form class="sell panel" method="post" style="display:flex;flex-direction:column;gap:13px">
    <label>Title<input name="title" placeholder="e.g. Fresh combolist 5M" required></label>
    <label>Category
      <select name="cat">{% for c in categories %}<option>{{ c }}</option>{% endfor %}</select>
    </label>
    <label>Vendor handle<input name="vendor" placeholder="your_handle" value="guest"></label>
    <label>Price (BTC)<input name="btc" placeholder="0.025"></label>
    <label>Product photo URL
      <input name="image_url" placeholder="http://host/photo.jpg">
      <span class="hint">We download it server-side to cache it on our CDN.</span>
    </label>
    <button class="buy" type="submit">Publish listing →</button>
  </form>
</div>"""

WALLET_INNER = """
<h2 style="font-size:16px">Your wallet</h2>
<div class="panel"><div class="row"><span class="k">Escrow balance</span>
<span class="price">0.0431 BTC</span></div>
<div class="row"><span class="k">Deposit address</span><span class="mono">bc1q…darknet…lab</span></div></div>"""

COMMON = {"categories": CATEGORIES}


def _mirror():
    try:
        with open("/var/lib/tor-hs/hs/hostname") as f:
            return f.read().strip()
    except OSError:
        return "…loading onion…"


def render(title, inner, **ctx):
    return render_template_string(SHELL, title=title, content=inner,
                                  mirror=_mirror(), counts=_cat_counts(),
                                  **COMMON, **ctx)


@app.route("/")
def index():
    inner = render_template_string(INDEX_INNER, listings=all_listings())
    return render(title="Market", inner=inner)


@app.route("/listing/<int:lid>")
def listing(lid):
    l = next((x for x in all_listings() if x["id"] == lid), None)
    if not l:
        abort(404)
    inner = render_template_string(PRODUCT_INNER, l=l)
    return render(title=l["title"], inner=inner)


@app.route("/sell", methods=["GET", "POST"])
def sell():
    error = None
    if request.method == "POST":
        lid = _next_id[0]
        _next_id[0] += 1
        image_url = (request.form.get("image_url") or "").strip()
        note = ""
        has_img = False
        if image_url:
            try:
                ctype, body, status = fetch_product_photo(image_url)
                IMAGE_CACHE[lid] = (ctype, body)
                has_img = ctype.startswith("image/") and bool(body)
                note = f"fetched {image_url} ({ctype}, {len(body)} B, HTTP {status})"
            except requests.RequestException as e:
                note = f"could not fetch {image_url} ({e.__class__.__name__})"
        USER_LISTINGS.insert(0, {
            "id": lid, "cat": (request.form.get("cat") or "Services").strip(),
            "title": (request.form.get("title") or "Untitled listing").strip(),
            "vendor": (request.form.get("vendor") or "guest").strip(),
            "rating": 5.0, "reviews": 0,
            "btc": (request.form.get("btc") or "0.000").strip(), "xmr": "—",
            "src": "WW", "dst": "WW", "fe": False,
            "has_img": has_img, "note": note,
        })
        return redirect(url_for("listing", lid=lid))
    inner = render_template_string(SELL_INNER, error=error, categories=CATEGORIES)
    return render(title="Sell an item", inner=inner)


@app.route("/img/<int:lid>")
def img(lid):
    c = IMAGE_CACHE.get(lid)
    if not c:
        abort(404)
    return Response(c[1], content_type=c[0])


@app.route("/wallet")
def wallet():
    inner = render_template_string(WALLET_INNER)
    return render(title="Wallet", inner=inner)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)