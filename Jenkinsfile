pipeline {
    agent any

    stages {
        stage('Build e Deploy') {
            steps {
                sh 'docker compose stop api-backend || true'
                sh 'docker compose rm -f api-backend || true'
                sh 'docker compose up -d --build --no-deps api-backend'
            }
        }
    }
}