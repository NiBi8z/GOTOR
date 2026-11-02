#!/bin/sh
# =============================================================================
# gen-keys.sh  -- Exec ONCE. Generating keys for lab.
#
# DA identities, relay ID, DirAuthority lines for ALL nodes
# =============================================================================
set -e
SHARED=/shared
ORPORT=9001
DIRPORT=9030

# /!\ THESE IP MUST MATCH docker-compose.yml
AUTHS="auth1:10.44.0.11 auth2:10.44.0.12 auth3:10.44.0.13"

if [ -f "$SHARED/dirauth.inc" ]; then
  echo "[keygen] dirauth.inc already here."
  exit 0
fi

mkdir -p "$SHARED/onions"
: > "$SHARED/dirauth.inc.tmp"

for entry in $AUTHS; do
  NICK=${entry%%:*}
  IP=${entry##*:}
  D="$SHARED/authkeys/$NICK"
  mkdir -p "$D/keys"
  chmod 700 "$D"

  echo "[keygen] === $NICK ($IP) ==="

  # gen auth cert
  printf '\n\n' | tor-gencert --create-identity-key -m 24 \
      -a "$IP:$DIRPORT" \
      -i "$D/keys/authority_identity_key" \
      -s "$D/keys/authority_signing_key" \
      -c "$D/keys/authority_certificate" \
      --passphrase-fd 0

  V3IDENT=$(awk '/^fingerprint /{print $2; exit}' "$D/keys/authority_certificate")

  # DA relay id
  timeout 8 tor --DataDirectory "$D" --ORPort "$ORPORT" --SocksPort 0 \
      --Nickname "$NICK" --PidFile "$D/tor.pid" \
      --Log "err stdout" >/dev/null 2>&1 || true

  if [ ! -f "$D/fingerprint" ]; then
    echo "[keygen] EROOR: No fingerprint for $NICK" >&2
    exit 1
  fi
  RELAYFP=$(awk '{print $2}' "$D/fingerprint")

  echo "DirAuthority $NICK orport=$ORPORT v3ident=$V3IDENT $IP:$DIRPORT $RELAYFP" \
      >> "$SHARED/dirauth.inc.tmp"
done

mv "$SHARED/dirauth.inc.tmp" "$SHARED/dirauth.inc"
chmod -R go+rX "$SHARED/authkeys" "$SHARED/dirauth.inc"

echo "[keygen] ================= dirauth.inc ================="
cat "$SHARED/dirauth.inc"
echo "[keygen] ================================================"
echo "[keygen] Done."
