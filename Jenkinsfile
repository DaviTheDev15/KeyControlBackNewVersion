pipeline {
    agent any

    stages {
        stage('Build e Deploy') {
            steps {
                sh 'docker stop api-backend'
                sh 'docker rm api-backend'
                sh 'docker compose up -d --build --no-deps api-backend'
            }
        }
    }
}