FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz libgraphviz-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11.29 /uv /uvx /bin/
ENV PYTHONUNBUFFERED=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
WORKDIR /workspace
