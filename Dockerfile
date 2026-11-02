# Simple image for relays
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      tor \
      python3 python3-pip \
      curl netcat-openbsd iproute2 procps ca-certificates jq \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir stem requests pysocks

COPY scripts/ /scripts/
RUN chmod +x /scripts/*.sh

ENTRYPOINT ["/scripts/entrypoint.sh"]
