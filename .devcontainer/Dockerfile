FROM mcr.microsoft.com/devcontainers/python:0-3.11

ENV PYTHONUNBUFFERED 1

COPY app/pyproject.toml /tmp/pip-tmp/

WORKDIR /tmp/pip-tmp/

RUN pip install poetry \
   && poetry config virtualenvs.create false \
   && poetry install \
   && rm -rf /tmp/pip-tmp

WORKDIR  /var/log/gunicorn
RUN chown -R vscode /var/log/gunicorn
