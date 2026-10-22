pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment {
        GITHUB_REPO = "baobao0303/Room_Agent"
        API_PORT    = "8765"
    }

    stages {
        stage('1. Anti-Leak & Security Sentinel Audit') {
            steps {
                sh '''
                    set -e
                    echo "=== Running Security Sentinel & Anti-Leak Gate ==="
                    python3 scripts/anti_leak_sentinel.py
                '''
            }
        }

        stage('2. SLPPC Governance Flow Audit') {
            steps {
                sh '''
                    set -e
                    echo "=== Running SLPPC Governance Flow Guard ==="
                    python3 tools/slppc_flow_guard.py
                '''
            }
        }

        stage('3. Self-Learning Knowledge Quality Audit') {
            steps {
                sh '''
                    set -e
                    echo "=== Auditing Harness Learn Knowledge Store ==="
                    python3 tools/harness_learning_search.py audit --threshold 0.60
                '''
            }
        }
    }
}
