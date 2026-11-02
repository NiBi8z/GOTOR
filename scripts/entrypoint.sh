#!/bin/sh
# =============================================================================
# 
# VAR:
#   TOR_ROLE  = auth | relay | client
#   TOR_NICK  = name of relay (uniq)
#   TOR_ADDR  = LAB IP FOR THIS RELAY
# =============================================================================
set -e

: "${TOR_ROLE:?TOR_ROLE missing}"
: "${TOR_NICK:?TOR_NICK missing}"

TOR_ADDR="${TOR_ADDR:-$(hostname -i | awk '{print $1}')}"

# DA uses  DataDirectory made by keygen 
if [ "$TOR_ROLE" = "auth" ]; then
  DATADIR="/shared/authkeys/$TOR_NICK"
else
  DATADIR="/var/lib/tor-node"
fi
mkdir -p "$DATADIR"
chmod 700 "$DATADIR"

# Relay/clients : removing state to avoid same guard accross lab reboot
if [ "$TOR_ROLE" != "auth" ]; then
  rm -f "$DATADIR/state"
fi

echo "[$TOR_NICK] waiting for /shared/dirauth.inc ..."
while [ ! -f /shared/dirauth.inc ]; do sleep 2; done
echo "[$TOR_NICK] dirauth.inc found, working on torrc."

TORRC=/tmp/torrc
{
  cat /torrc/common.torrc
  echo
  cat "/torrc/${TOR_ROLE}.torrc"
  echo
  # No sticky guard for DA.
  [ "$TOR_ROLE" != "auth" ] && cat /torrc/entry-guards.inc
  echo
  echo "Nickname $TOR_NICK"
  echo "DataDirectory $DATADIR"
  echo "Address $TOR_ADDR"
  echo
  cat /shared/dirauth.inc
} > "$TORRC"

echo "[$TOR_NICK] ---- torrc ----"
sed 's/^/[torrc] /' "$TORRC"
echo "[$TOR_NICK] ------------------------"

exec tor -f "$TORRC"
