FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.11.29 /uv /uvx /bin/
ENV PYTHONUNBUFFERED=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
WORKDIR /workspace
