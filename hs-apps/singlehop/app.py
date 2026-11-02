#!/usr/bin/env python3

import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def onion_addr():
    try:
        with open("/var/lib/tor-hs/hs/hostname") as f:
            return f.read().strip()
    except OSError:
        return "………………………………………………………….onion"


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>n0cturn :: ghost node</title>
<style>
:root{--bg:#04060a;--ink:#0affc2;--ink2:#06b88c;--dim:#1b5a4c;--mut:#2f5e55;
--red:#ff4d5e;--amber:#ffcc4d;--line:#0d2a24}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);
font-family:ui-monospace,"JetBrains Mono","Fira Code",Menlo,Consolas,monospace;
font-size:15px;line-height:1.6;overflow-x:hidden;
text-shadow:0 0 6px rgba(10,255,194,.35)}
/* scanlines + vignette CRT */
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:9;
background:repeating-linear-gradient(0deg,rgba(0,0,0,0) 0 2px,rgba(0,0,0,.25) 2px 3px)}
body::after{content:"";position:fixed;inset:0;pointer-events:none;z-index:9;
background:radial-gradient(120% 90% at 50% 40%,transparent 55%,rgba(0,0,0,.75) 100%)}
.wrap{max-width:820px;margin:0 auto;padding:46px 22px 80px;position:relative;z-index:1}
.sys{color:var(--mut);font-size:12.5px;letter-spacing:.5px}
.sys .ok{color:var(--ink)}.sys .warn{color:var(--amber)}
pre.logo{color:var(--ink);line-height:1.1;font-size:12px;margin:18px 0 8px;
filter:drop-shadow(0 0 10px rgba(10,255,194,.5))}
h1{font-size:30px;margin:14px 0 4px;letter-spacing:2px;color:#d7fff2}
h1 .glow{color:var(--ink)}
.tagline{color:var(--ink2);font-size:17px;margin:0 0 26px}
.tagline .cur{display:inline-block;width:9px;height:17px;background:var(--ink);
margin-left:3px;vertical-align:-2px;animation:blink 1.05s step-end infinite}
@keyframes blink{50%{opacity:0}}
.panel{border:1px solid var(--line);border-left:3px solid var(--ink2);
background:rgba(6,30,25,.35);border-radius:4px;padding:16px 18px;margin:16px 0}
.panel h3{margin:0 0 10px;font-size:12px;letter-spacing:2px;text-transform:uppercase;color:var(--dim)}
.kv{display:flex;justify-content:space-between;gap:16px;padding:3px 0;border-bottom:1px dotted var(--line);font-size:13.5px}
.kv:last-child{border:0}.kv .k{color:var(--mut)}
.kv .v{color:var(--ink)}.kv .v.red{color:var(--red)}.kv .v.amber{color:var(--amber)}
.manifesto{color:#9fe9d8;font-size:14px}
.manifesto b{color:#d7fff2}
.term{background:#02110d;border:1px solid var(--line);border-radius:4px;padding:14px 16px;margin:16px 0;font-size:13px;color:var(--ink2)}
.term .p{color:var(--dim)}
.term .c{color:#d7fff2}
.boast{font-size:20px;color:#d7fff2;margin:30px 0 6px;letter-spacing:.5px}
.sub{color:var(--mut);font-size:12.5px}
.onion{word-break:break-all;color:var(--ink)}
footer{margin-top:40px;color:var(--mut);font-size:11.5px;border-top:1px solid var(--line);padding-top:14px}
a{color:var(--ink)}
</style></head>
<body><div class="wrap">

<div class="sys">[ boot ] tor circuit established &nbsp;·&nbsp; <span class="ok">rendezvous OK</span>
&nbsp;·&nbsp; latency <span class="warn">7ms</span> &nbsp;·&nbsp; location <span class="ok">/dev/null</span></div>

<pre class="logo">
      _   ___   ____ _____ _   _ ____  _   _
     | \\ | / _ \\ / ___|_   _| | | |  _ \\| \\ | |
     |  \\| | | | | |     | | | | | | |_) |  \\| |
     | |\\  | |_| | |___  | | | |_| |  _ &lt;| |\\  |
     |_| \\_|\\___/ \\____| |_|  \\___/|_| \\_\\_| \\_|
</pre>

<h1>n0cturn<span class="glow">//</span>ghost node</h1>
<p class="tagline">you can't trace what doesn't exist<span class="cur"></span></p>

<p class="manifesto">No name. No logs. No jurisdiction. This box lives <b>behind the onion</b> —
three hops of cryptography between you and a shadow. Subpoena the void. Knock on
<code>/dev/null</code>. You will get <b>nothing</b>, because there is <b>nowhere</b> to knock.</p>

<div class="panel">
  <h3>node :: status</h3>
  <div class="kv"><span class="k">handle</span><span class="v">n0cturn</span></div>
  <div class="kv"><span class="k">reachable at</span><span class="v onion">{{ONION}}</span></div>
  <div class="kv"><span class="k">physical location</span><span class="v">UNKNOWN — routed through Tor</span></div>
  <div class="kv"><span class="k">real ip</span><span class="v red">[ redacted · unroutable ]</span></div>
  <div class="kv"><span class="k">operator</span><span class="v">ghost — catch me if you can</span></div>
  <div class="kv"><span class="k">mode</span><span class="v amber">performance / low-latency ⚡</span></div>
</div>

<div class="term">
<div><span class="p">root@ghost:~#</span> <span class="c">whoami</span></div>
<div>nobody</div>
<div><span class="p">root@ghost:~#</span> <span class="c">curl ifconfig.me</span></div>
<div>curl: (7) could not resolve — this node does not reach out. ever.</div>
<div><span class="p">root@ghost:~#</span> <span class="c">traceroute ghost</span></div>
<div>* * *  &nbsp; * * *  &nbsp; * * *  &nbsp; [ hops lost in the dark ]</div>
</div>

<p class="boast">Think you can find the box behind this onion?</p>
<p class="sub">Go ahead. Follow the circuit. I optimized it for <b>speed</b>, not for you.</p>

<footer>
n0cturn ghost node · onion-only · no analytics · no cookies · no mercy<br>
“the net interprets censorship as damage and routes around it.” — stay invisible.
</footer>

</div></body></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = PAGE.replace("{{ONION}}", onion_addr()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8080), H).serve_forever()
