pipeline {
    agent any

    stages {
        stage('Build e Deploy') {
            steps {
                sh 'docker compose -f docker-compose.backend.yml down'
                sh 'docker compose -f docker-compose.backend.yml up -d --build'
            }
        }
    }
}