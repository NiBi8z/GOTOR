FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      tor python3 python3-pip iproute2 curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages --no-cache-dir flask requests
COPY app.py /app/app.py
COPY hs-entrypoint.sh /hs-entrypoint.sh
RUN chmod +x /hs-entrypoint.sh
ENTRYPOINT ["/hs-entrypoint.sh"]
