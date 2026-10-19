# Deleted Configs Backup (`projects/aevum`)

Archived: 2026-10-18
Purpose: Restore files if ever deploying to Render, CodeSandbox, or DevContainer.

---

## 1. `render.yaml`
```yaml
services:
  - type: web
    name: aevum
    runtime: image
    image:
      url: ghcr.io/aevum/aevum:stable
    plan: standard
    envVars:
      - key: PORT
        value: 3010
      - key: DATABASE_URL
        fromDatabase:
          name: aevum-db
          property: connectionString
      - key: REDIS_SERVER_URL
        fromService:
          type: redis
          name: aevum-redis
          property: connectionString
```

## 2. `.render/Dockerfile`
```dockerfile
FROM ghcr.io/aevum/aevum:stable
COPY .render/start.sh /app/start.sh
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
```

## 3. `.render/start.sh`
```bash
#!/bin/sh
set -e
node ./scripts/self-host-predeploy.js
exec node ./dist/index.js
```

## 4. `.codesandbox/task.json`
```json
{
  "$schema": "https://codesandbox.io/schemas/tasks.json",
  "setupTasks": [
    {
      "name": "Install Dependencies",
      "command": "yarn install"
    }
  ],
  "tasks": {
    "start-web": {
      "name": "Start Web",
      "command": "yarn dev-core",
      "runAtStart": true,
      "preview": {
        "port": 8080
      }
    }
  }
}
```

## 5. `tsconfig.eslint.json`
```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "allowJs": true
  },
  "include": [
    ".",
    ".github/actions/*/*.mjs",
    "blocksuite/docs-site/.vitepress/**/*.ts"
  ],
  "exclude": [
    "**/target",
    "**/node_modules",
    "**/dist",
    "**/lib",
    ".coverage",
    ".yarn",
    "**/test-results",
    "**/web-static"
  ]
}
```

## 6. `.devcontainer/devcontainer.json`
```json
{
  "name": "AFFiNE Dev Container",
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspaces/${localWorkspaceFolderBasename}",
  "containerEnv": {
    "COREPACK_ENABLE_DOWNLOAD_PROMPT": "0"
  },
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "lts",
      "installYarnUsingApt": false
    },
    "ghcr.io/devcontainers/features/rust:1": {}
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-playwright.playwright",
        "oxc.oxc-vscode"
      ]
    }
  },
  "updateContentCommand": "bash ./.devcontainer/build.sh",
  "postCreateCommand": "bash ./.devcontainer/setup-user.sh"
}
```

## 7. `.devcontainer/docker-compose.yml`
```yaml
version: '3.8'
services:
  app:
    security_opt:
      - no-new-privileges:true
    image: mcr.microsoft.com/devcontainers/base:bookworm
    volumes:
      - ../..:/workspaces:cached
    command: sleep infinity
    network_mode: service:db
    environment:
      DATABASE_URL: postgresql://affine:affine@db:5432/affine
      REDIS_SERVER_HOST: redis
  db:
    image: pgvector/pgvector:pg16
    restart: unless-stopped
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: affine
      POSTGRES_USER: affine
      POSTGRES_DB: affine
  redis:
    image: redis
volumes:
  postgres-data:
```

## 8. `.devcontainer/build.sh`
```bash
#!/bin/bash
yarn install
yarn affine @affine/server-native build
yarn affine @affine/server prisma migrate reset -f
```

## 9. `.devcontainer/setup-user.sh`
```bash
set -e
npm install -g @withgraphite/graphite-cli@stable
if [ -v GRAPHITE_TOKEN ];then
  gt auth --token $GRAPHITE_TOKEN
fi
gt init --trunk canary
```
