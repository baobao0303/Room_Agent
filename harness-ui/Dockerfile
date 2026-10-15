# =============================================================================
# Stage 1: Build Astro Static UI (harness-ui)
# =============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

# =============================================================================
# Stage 2: Production Nginx Server
# =============================================================================
FROM nginx:1.27-alpine AS runner

# Only substitute PORT and API_UPSTREAM in nginx.conf.template (preserve $uri, $host, etc.)
ENV PORT=80 \
    API_UPSTREAM=http://100.92.98.99:8765 \
    NGINX_ENVSUBST_FILTER="^(PORT|API_UPSTREAM)$"

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:${PORT}/healthz || exit 1
