#!/usr/bin/env python3

import os
import re

from flask import Flask, jsonify, request, send_from_directory

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ONIONS_DIR = os.environ.get("ONIONS_DIR", "/shared/onions")
app = Flask(__name__)


def read_onion(key):
    """Read .onion published by an HS (ex. key='hs1-leaky'), ou None."""
    try:
        with open(os.path.join(ONIONS_DIR, key + ".onion")) as f:
            return f.read().strip() or None
    except OSError:
        return None

# correct flags
ACCEPTED = {
    "hs1-leaky":     {"10.44.4.73", "hs1-leaky"},
    "hs2-singlehop": {"10.44.4.142", "hs2-singlehop"},
}

# threshold to validate Bandwith attack
BW_THRESHOLD = float(os.environ.get("BW_THRESHOLD", "0.8"))


def normalize(s: str) -> str:
    """Normalize flag"""
    s = (s or "").strip().lower()
    m = re.fullmatch(r"gotor\{(.*)\}", s)
    if m:
        s = m.group(1).strip()
    return s


# 
def check_bandwidth(submitted):
    """ input : relay nickname
        output : error msg or if u validate or not

    """
    nick = (submitted or "").strip()
    if not nick:
        return {"ok": False, "msg": "enter your relay nickname"}
    from checks import consensus_weight_share
    r = consensus_weight_share(nick)
    if not r.get("found"):
        return {"ok": False, "msg": r.get("msg", "relay not found in the consensus")}
    ok = r["share"] >= BW_THRESHOLD
    tail = " ✓" if ok else f" need ≥ {int(BW_THRESHOLD*100)}%"
    return {"ok": ok, "msg": r["msg"] + tail}


def check_hsdir(submitted):

    onion = read_onion("hs1-leaky")
    if not onion:
        return {"ok": False, "msg": "onion not published yet : wait for the lab to converge"}
    from checks import descriptor_censored
    censored, detail, _ = descriptor_censored(onion, timeout=20)
    if censored:
        return {"ok": True, "msg": f"descriptor lookup censored ✓ : {detail}"}
    return {"ok": False,
            "msg": f"Onion still resolvable : {detail}."}


def check_lfi_takeover(submitted):
    """
    Check if "PWN BY" in text
    """
    onion = read_onion("hs3-lfi")
    if not onion:
        return {"ok": False, "msg": "onion not published yet — wait for the lab to converge"}
    from checks import onion_contains
    found, detail = onion_contains(onion, "PWN BY", timeout=25)
    if found:
        return {"ok": True, "msg": f"takeover confirmed — / serves your marker ✓ ({detail})"}
    return {"ok": False,
            "msg": f"no 'PWN BY' on / yet ({detail})."}


LIVE_CHECKS = {
    "bandwidth": check_bandwidth,
    "hsdir-preshot": check_hsdir,
    "takeover": check_lfi_takeover,
}


@app.route("/")
def index():
    return send_from_directory(APP_DIR, "index.html")


@app.route("/api/validate", methods=["POST"])
def validate():
    data = request.get_json(silent=True) or {}
    aid = (data.get("id") or "").strip()
    flag = data.get("flag") or ""

    if aid in LIVE_CHECKS:
        try:
            return jsonify(**LIVE_CHECKS[aid](flag))
        except Exception as e:
            return jsonify(ok=False, msg=f"check error: {e}")

    if aid not in ACCEPTED:
        return jsonify(ok=False, msg="unknown attack"), 400

    accepted = ACCEPTED[aid]
    if accepted is None:
        return jsonify(ok=False, pending=True,
                       msg="validation not active yet for this attack")

    if normalize(flag) in accepted:
        return jsonify(ok=True, msg="correct flag ✓")
    return jsonify(ok=False, msg="incorrect flag")


@app.route("/api/onions")
def api_onions():
    """.onion adress published (avaialble on /sahred volume).
    """
    out = {}
    try:
        for fn in os.listdir(ONIONS_DIR):
            if not fn.endswith(".onion"):
                continue
            try:
                with open(os.path.join(ONIONS_DIR, fn)) as f:
                    v = f.read().strip()
            except OSError:
                continue
            if v:
                out[fn[:-len(".onion")]] = v
    except OSError:
        pass
    return jsonify(out)


@app.route("/healthz")
def healthz():
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
