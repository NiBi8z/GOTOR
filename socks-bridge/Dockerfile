# Basic dockerfile just to socat host to lab network using client1
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends socat \
 && rm -rf /var/lib/apt/lists/*
CMD ["socat", "TCP-LISTEN:9050,fork,reuseaddr", "TCP:client1:9050"]
