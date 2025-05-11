# Stage 1: Plugin Builder
FROM python:3.11-slim AS builder

WORKDIR /build
ENV LOGFILE="install_plugins1.log"

# Install build tools and PEP 517/518 support
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential python3-pip && \
    pip install build && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy plugin source folders (assumed to be one level above Dockerfile)
COPY ./ ./plugins
# Build all plugin wheel files
RUN mkdir -p /dist && \
    for d in ./plugins/*; do \
        if [ -d "$d" ] && ls "$d"/*.toml >/dev/null 2>&1; then \
            echo "📦 Building plugin: $d" | tee -a "$LOGFILE"; \
            ls -l "$d" | tee -a "$LOGFILE"; \
            cd "$d"; \
            echo "Installing dependencies and building wheel in $d..." | tee -a "$LOGFILE"; \
            python3 -m build . --wheel --outdir dist >> "$LOGFILE" 2>&1 && \
            cp dist/*.whl /dist/ || echo "❌ Failed to build $d" | tee -a "$LOGFILE"; \
            cd - > /dev/null; \
        else \
            echo "⚠️ Skipping $d: Not a directory or no *.toml file" | tee -a "$LOGFILE"; \
        fi; \
    done
# Stage 2: Final App Image


FROM lyikprodblueacr.azurecr.io/lyik-api:latest
ENV LOGFILE1="/plugin_logs/install_plugins1.log"
COPY --from=builder /build/install_plugins1.log /plugin_logs/install_plugins1.log
COPY --from=builder /dist/*.whl /dist/ 
RUN pip3 install -v /dist/*.whl | tee -a $LOGFILE1

EXPOSE 8080
ENTRYPOINT ["/app/start.sh"]