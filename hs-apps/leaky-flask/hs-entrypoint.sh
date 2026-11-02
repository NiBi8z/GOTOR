#!/bin/sh
# Publish onion
set -e
: "${HS_NICK:?}"; : "${HS_ADDR:?}"; : "${HS_NAME:?}"; : "${HS_VARIANT:=default}"

DATADIR=/var/lib/tor-hs
mkdir -p "$DATADIR/hs"
chmod 700 "$DATADIR" "$DATADIR/hs"

echo "[$HS_NICK] waiting for dirauth.inc ..."
while [ ! -f /shared/dirauth.inc ]; do sleep 2; done
.
python3 /app/app.py &

HS_EXTRA=""
if [ "$HS_VARIANT" = "singlehop" ]; then
  HS_EXTRA="HiddenServiceNonAnonymousMode 1
HiddenServiceSingleHopMode 1"
fi

TORRC=/tmp/torrc
{
  cat /torrc/common.torrc
  echo
  echo "ORPort 0"
  echo "SocksPort 0"
  echo "Nickname $HS_NICK"
  echo "DataDirectory $DATADIR"
  echo "Address $HS_ADDR"
  echo "HiddenServiceDir $DATADIR/hs"
  echo "HiddenServicePort 80 127.0.0.1:8080"
  [ -n "$HS_EXTRA" ] && echo "$HS_EXTRA"
  [ "$HS_VARIANT" != "singlehop" ] && cat /torrc/entry-guards.inc
  echo
  cat /shared/dirauth.inc
} > "$TORRC"

(
  while [ ! -s "$DATADIR/hs/hostname" ]; do sleep 1; done
  mkdir -p /shared/onions
  cp "$DATADIR/hs/hostname" "/shared/onions/${HS_NAME}.onion"
  echo "[$HS_NICK] ONION = $(cat "$DATADIR/hs/hostname")"
) &

exec tor -f "$TORRC"
