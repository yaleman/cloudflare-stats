# https://github.com/casey/just

# list things
default: list

# List the options
list:
    just --list

# Build the docker image locally using buildx
docker_buildx:
    docker buildx build \
        --tag ghcr.io/yaleman/cloudflare-stats:latest \
        --label org.opencontainers.image.source=https://github.com/yaleman/cloudflare-stats \
        --label org.opencontainers.image.revision=$(git rev-parse HEAD) \
        --label org.opencontainers.image.created=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
        .

# Build the docker image locally
docker_build:
    docker build \
        --tag ghcr.io/yaleman/cloudflare-stats:latest \
        --tag ghcr.io/yaleman/cloudflare-stats:$(git rev-parse HEAD) \
        --label org.opencontainers.image.source=https://github.com/yaleman/cloudflare-stats \
        --label org.opencontainers.image.revision=$(git rev-parse HEAD) \
        --label org.opencontainers.image.created=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
        .

# Publish multi-arch docker image to ghcr.io
docker_publish:
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --tag ghcr.io/yaleman/cloudflare-stats:latest \
        --tag ghcr.io/yaleman/cloudflare-stats:$(git rev-parse HEAD) \
        --label org.opencontainers.image.source=https://github.com/yaleman/cloudflare-stats \
        --label org.opencontainers.image.revision=$(git rev-parse HEAD) \
        --label org.opencontainers.image.created=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
        --push \
        .

# Publish a dev build
docker_publish_dev:
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --tag ghcr.io/yaleman/cloudflare-stats:dev \
        --tag ghcr.io/yaleman/cloudflare-stats:$(git rev-parse HEAD) \
        --label org.opencontainers.image.source=https://github.com/yaleman/cloudflare-stats \
        --label org.opencontainers.image.revision=$(git rev-parse HEAD) \
        --label org.opencontainers.image.created=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
        --push \
        .

# Run a local debug instance
run:
    uv run cloudflare-analytics

# Run in docker
run_docker:
    docker run -it --rm \
        --init \
        --mount "type=bind,source=$HOME/.config/cloudflare-stats.json,target=/cloudflare-stats.json" \
        ghcr.io/yaleman/cloudflare-stats:latest

# Run all the checks
check: codespell test


# Spell check the things
codespell:
    codespell -c \
    --ignore-words .codespell_ignore \
    --skip='./.venv'

test:
    uv run pytest
lint:
    uv run mypy --strict cloudflare_stats tests
    uv run ruff check cloudflare_stats tests


# Semgrep things
semgrep:
    semgrep ci --config auto \
    --exclude-rule "yaml.github-actions.security.third-party-action-not-pinned-to-commit-sha.third-party-action-not-pinned-to-commit-sha" \
    --exclude-rule "generic.html-templates.security.var-in-script-tag.var-in-script-tag" \
    --exclude-rule "javascript.express.security.audit.xss.mustache.var-in-href.var-in-href" \
    --exclude-rule "python.django.security.django-no-csrf-token.django-no-csrf-token" \
    --exclude-rule "python.django.security.audit.xss.template-href-var.template-href-var" \
    --exclude-rule "python.django.security.audit.xss.var-in-script-tag.var-in-script-tag" \
    --exclude-rule "python.flask.security.xss.audit.template-href-var.template-href-var" \
    --exclude-rule "python.flask.security.xss.audit.template-href-var.template-href-var"

# Run trivy on the repo
trivy_repo:
    trivy repo $(pwd) --skip-files .envrc -d