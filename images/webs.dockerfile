FROM python:3.12.6-alpine3.20

# Development deps needed so KERIpy can see libsodium (dynamically linked at runtime)
RUN apk --no-cache add \
    bash \
    alpine-sdk \
    libsodium-dev

# Add uv build tool
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy in KERIpy from weboftrust image
COPY --from=weboftrust/keri:1.2.6 /keripy /keripy
COPY --from=weboftrust/keri:1.2.6 /keripy/src /keripy/src

ENV PATH="/keripy/venv/bin:${PATH}"
# Ignore the syntax warning for KERIpy's old regex usage
ENV PYTHONWARNINGS="ignore::SyntaxWarning"

# Install dkr - did KERI resolver
WORKDIR /usr/local/var

RUN mkdir -p /usr/local/var/webs
COPY . /usr/local/var/webs

WORKDIR /usr/local/var/webs

# Lock and install dkr
RUN uv lock && \
    uv sync --locked

ENV PATH="/usr/local/var/webs/.venv/bin:$PATH"

WORKDIR /usr/local/var/webs/volume/dkr/examples