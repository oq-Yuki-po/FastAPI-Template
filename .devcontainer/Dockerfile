# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.191.1/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version: 3, 3.9, 3.8, 3.7, 3.6
ARG VARIANT="3.9"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

ENV PYTHONPATH "${PYTHONPATH}:/workspaces/FastAPI-Template"

COPY app/pyproject.toml app/poetry.lock /tmp/pip-tmp/

WORKDIR /tmp/pip-tmp/

RUN pip install poetry \
   && poetry config virtualenvs.create false \
   && poetry install \
   && rm -rf /tmp/pip-tmp
