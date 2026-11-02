#!/usr/bin/env python3

import os

from flask import Flask, Response, redirect, request

app = Flask(__name__)
PAGES_DIR = "/app/pages"


@app.route("/")
def home():
    return redirect("/page?f=home.html", code=302)


@app.route("/page")
def page():
    f = request.args.get("f", "home.html")
    path = os.path.join(PAGES_DIR, f) # ooops
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return Response(f"page not found: {f}\n", status=404,
                        content_type="text/plain; charset=utf-8")

    ctype = ("text/html; charset=utf-8" if f.lower().endswith(".html")
             else "text/plain; charset=utf-8")
    return Response(data, content_type=ctype)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)