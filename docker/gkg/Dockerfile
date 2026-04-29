FROM ubuntu:24.04

RUN apt-get update && apt-get install -y curl git ca-certificates bash && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://gitlab.com/gitlab-org/rust/knowledge-graph/-/raw/main/install.sh | bash
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /workspace

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 27495

ENTRYPOINT ["/entrypoint.sh"]
