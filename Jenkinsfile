pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment {
        GITHUB_REPO      = "baobao0303/Room_Agent"
        GHCR_IMAGE       = "ghcr.io/baobao0303/room_agent/harness-ui:latest"
        RELEASE_TAG      = "harness-ui-latest"
        CONTAINER_NAME   = "paseo-harness-ui"
        UI_PORT          = "4321"
        API_PORT         = "8765"
        BACKEND_UPSTREAM = "http://100.92.98.99:8765"
    }

    stages {
        stage('1. Pull Pre-built Docker Image from GitHub') {
            steps {
                sh '''
                    set -e
                    echo "=== Pulling pre-built Harness UI Docker image from GitHub ==="
                    if docker pull ${GHCR_IMAGE}; then
                        docker tag ${GHCR_IMAGE} harness-ui:latest
                        echo "✓ Pulled image directly from GHCR: ${GHCR_IMAGE}"
                    else
                        echo "GHCR requires auth or not public yet, pulling pre-built Docker archive from GitHub Release..."
                        curl -fSL "https://github.com/${GITHUB_REPO}/releases/download/${RELEASE_TAG}/harness-ui-docker-latest.tar.gz" | gunzip | docker load
                        echo "✓ Loaded pre-built Docker image from GitHub Release (${RELEASE_TAG})"
                    fi
                '''
            }
        }

        stage('2. Pull Pre-built Astro Dist for Local Dashboard Fallback') {
            steps {
                sh '''
                    set -e
                    mkdir -p "${WORKSPACE}/harness-ui/dist"
                    if curl -fSL "https://github.com/${GITHUB_REPO}/releases/download/${RELEASE_TAG}/harness-ui-dist.tar.gz" -o /tmp/harness-ui-dist.tar.gz; then
                        tar -xzf /tmp/harness-ui-dist.tar.gz -C "${WORKSPACE}/harness-ui/dist"
                        rm -f /tmp/harness-ui-dist.tar.gz
                        echo "✓ Extracted pre-built Astro dist into harness-ui/dist/"
                    fi
                '''
            }
        }

        stage('3. Start Harness Backend API & Deploy UI Container') {
            steps {
                sh '''
                    set -e
                    # Ensure Python Backend API is running on port 8765
                    python3 scripts/harness_dashboard.py --daemon --port ${API_PORT} || true

                    # Restart Docker container for Harness UI
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --restart unless-stopped \
                        -p ${UI_PORT}:80 \
                        -e API_UPSTREAM=${BACKEND_UPSTREAM} \
                        harness-ui:latest
                '''
            }
        }

        stage('4. Smoke Test UI Container') {
            steps {
                sh '''
                    set -e
                    sleep 2
                    curl -fsS "http://127.0.0.1:${UI_PORT}/healthz"
                    curl -fsS "http://127.0.0.1:${UI_PORT}/" | head -n 5
                    echo "✓ Harness UI container is healthy at http://127.0.0.1:${UI_PORT}"
                '''
            }
        }
    }
}
