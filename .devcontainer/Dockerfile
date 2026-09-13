ARG GO_VERSION=1.26.7

FROM golang:${GO_VERSION}-bookworm AS task-tui-builder

ARG TASK_TUI_REF=f96f3c88be6d2936be8b7bf7b1c6929b15a67c14

WORKDIR /src/task

RUN git init \
    && git remote add origin https://github.com/janluke/task.git \
    && git fetch --depth 1 origin "${TASK_TUI_REF}" \
    && git checkout --detach FETCH_HEAD

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    for attempt in 1 2 3; do \
        CGO_ENABLED=0 go build -trimpath -o /out/task-tui ./cmd/task && exit 0; \
        if [ "${attempt}" -eq 3 ]; then exit 1; fi; \
        sleep 5; \
    done


FROM mcr.microsoft.com/devcontainers/python:3-3.10-bookworm

ARG HATCH_VERSION=1.18.0
ARG TASK_VERSION=v3.53.1

USER root

RUN pipx install "hatch==${HATCH_VERSION}" \
    && curl --fail --location --silent --show-error \
        https://taskfile.dev/install.sh \
        --output /tmp/install-task.sh \
    && sh /tmp/install-task.sh -b /usr/local/bin "${TASK_VERSION}" \
    && rm /tmp/install-task.sh \
    && task --version

COPY --from=task-tui-builder /out/task-tui /usr/local/bin/task-tui

RUN task-tui --version \
    && printf "\nalias tui='task-tui --tui'\n" >> /etc/bash.bashrc \
    && printf "\nalias tui='task-tui --tui'\n" >> /etc/zsh/zshrc

USER vscode
