#!/usr/bin/env python3

import os
import socket
import threading

import requests
from stem.control import Controller, EventType

CLIENT = os.environ.get("CHECK_CLIENT", "client2")
CTRL_PORT = int(os.environ.get("CHECK_CONTROL_PORT", "9051"))
SOCKS_PORT = int(os.environ.get("CHECK_SOCKS_PORT", "9050"))
PASSWORD = os.environ.get("TOR_CONTROL_PASSWORD", "goadtor-dashboard-lab")


def client_controller(client=None):
    """Auth to client ControlPort."""
    addr = socket.gethostbyname(client or CLIENT)
    c = Controller.from_port(address=addr, port=CTRL_PORT)
    c.authenticate(password=PASSWORD)
    return c


def onion_contains(onion, needle, client=None, timeout=25):
    """GET http://<onion>/ via a lab client and test if `needle` is in the body.

    Returns (found: bool, detail: str).
    """
    addr = onion[:-6] if onion.lower().endswith(".onion") else onion
    try:
        with client_controller(client) as c:
            try:
                c.get_hidden_service_descriptor(addr, await_result=True,
                                                timeout=min(timeout, 20))
            except Exception:
                pass  
    except Exception:
        pass
    sock = f"socks5h://{client or CLIENT}:{SOCKS_PORT}"
    try:
        r = requests.get(f"http://{onion}/",
                         proxies={"http": sock, "https": sock}, timeout=timeout)
        return (needle.lower() in r.text.lower()), f"HTTP {r.status_code}, {len(r.text)} B"
    except requests.exceptions.RequestException as e:
        return False, f"fetch failed ({type(e).__name__})"


def descriptor_censored(onion, client=None, timeout=20):
    """ Send HSFETCH to see if descriptor is reachable or not
    Returns: (censored: bool, detail: str, hsdirs: list[(fp, action)])."""
    addr = onion[:-6] if onion.lower().endswith(".onion") else onion
    state = {"received": False, "requested": 0, "failed": 0}
    hsdirs = []
    done = threading.Event()

    def on_evt(e):
        act = getattr(e, "action", "")
        fp = getattr(e, "directory_fingerprint", None)
        if fp:
            hsdirs.append((fp, act))
        if act in ("RECEIVED", "CONTENT"):
            state["received"] = True
            done.set()
        elif act == "REQUESTED":
            state["requested"] += 1
        elif act == "FAILED":
            state["failed"] += 1

    with client_controller(client) as c:
        c.add_event_listener(on_evt, EventType.HS_DESC)
        try:
            # await_result=False
            c.get_hidden_service_descriptor(addr, await_result=False)
        except Exception:
            pass
        done.wait(timeout)

    if state["received"]:
        return False, "descriptor received from an HSDir", hsdirs
    if state["requested"]:
        return True, f"{state['failed']} HSDir fetch(es) failed, 0 received", hsdirs
    return True, "no HSDir responded", hsdirs


def consensus_weight_share(nick, client=None):
    """
    Check relay weight share
    """
    nick_l = (nick or "").strip().lower()
    res = {"relay": nick, "found": False, "running": False,
           "weight": 0, "total": 0, "share": 0.0, "n": 0}

    with client_controller(client) as c:
        entries = list(c.get_network_statuses())

    total = 0
    mine = None
    for e in entries:
        if "Running" not in e.flags:
            continue
        total += (e.bandwidth or 0)          # 'w Bandwidth=' du consensus
        if e.nickname and e.nickname.lower() == nick_l:
            mine = e

    res["n"] = len(entries)
    res["total"] = total
    if mine is None:
        res["msg"] = f"relay '{nick}' not found (or not Running) in the consensus"
        return res

    res["found"] = True
    res["running"] = "Running" in mine.flags
    res["weight"] = mine.bandwidth or 0
    res["fingerprint"] = mine.fingerprint
    res["share"] = (res["weight"] / total) if total else 0.0
    res["msg"] = (f"your relay holds {res['share']*100:.0f}% of the consensus "
                  f"weight ({res['weight']}/{total})")
    return res
