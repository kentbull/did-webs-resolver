ARG KERI_IMAGE=gleif/keri:1.2.18@sha256:dcf31bdbff69cbb5d69abbedebdcf6c203bfdbb95f5f582432b2d6359e331793
FROM ${KERI_IMAGE} AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /bin/uv
RUN apk add --no-cache build-base patch
WORKDIR /dws
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-editable --no-install-project
COPY src/ src/
RUN uv sync --locked --no-dev --no-editable

FROM ${KERI_IMAGE}
RUN apk add --no-cache curl jq
WORKDIR /dws
COPY . /dws
COPY --from=builder /dws/.venv /dws/.venv
ENV PATH="/dws/.venv/bin:$PATH"
ENV PYTHONWARNINGS="ignore::SyntaxWarning"
ENTRYPOINT []
