FROM rust:1.94-bookworm

WORKDIR /workspace

RUN apt-get update \
  && apt-get install -y --no-install-recommends pkg-config libssl-dev ca-certificates \
  && rm -rf /var/lib/apt/lists/*

CMD ["cargo", "run", "-p", "raptorflow-api"]
