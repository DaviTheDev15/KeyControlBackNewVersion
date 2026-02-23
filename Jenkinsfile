pipeline {
    agent any

    stages {
        stage('Build e Deploy') {
            steps {
                sh 'docker compose -f docker-compose.backend.yml -p backend down'
                sh 'docker compose -f docker-compose.backend.yml -p backend up -d --build'
            }
        }
    }
}