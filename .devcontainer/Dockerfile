FROM mcr.microsoft.com/devcontainers/python:3-3.10-bookworm

ARG HATCH_VERSION=1.18.0
ARG TASK_VERSION=v3.53.1
ARG TASK_TUI_VERSION=tui-v0.1.0-task-v3.53.1

USER root

RUN pipx install "hatch==${HATCH_VERSION}" \
    && curl --fail --location --silent --show-error \
        https://taskfile.dev/install.sh \
        --output /tmp/install-task.sh \
    && sh /tmp/install-task.sh -b /usr/local/bin "${TASK_VERSION}" \
    && rm /tmp/install-task.sh \
    && task --version

# Unofficial Task build with the TUI, from https://github.com/janluke/task-tui.
# It installs as `task-tui`, leaving the official `task` above untouched.
RUN architecture="$(dpkg --print-architecture)" \
    && case "${architecture}" in \
        amd64|arm64) archive="task-tui_linux_${architecture}.tar.gz" ;; \
        *) echo "Unsupported architecture: ${architecture}" >&2; exit 1 ;; \
    esac \
    && release_url="https://github.com/janluke/task-tui/releases/download/${TASK_TUI_VERSION}" \
    && curl --fail --location --silent --show-error \
        "${release_url}/${archive}" --output "/tmp/${archive}" \
    && curl --fail --location --silent --show-error \
        "${release_url}/checksums.txt" --output /tmp/checksums.txt \
    && (cd /tmp && sha256sum --check --ignore-missing checksums.txt) \
    && tar -xzf "/tmp/${archive}" -C /usr/local/bin task-tui \
    && rm "/tmp/${archive}" /tmp/checksums.txt \
    && task-tui --version \
    && printf "\nalias tui='task-tui --tui'\n" >> /etc/bash.bashrc \
    && printf "\nalias tui='task-tui --tui'\n" >> /etc/zsh/zshrc

USER vscode
