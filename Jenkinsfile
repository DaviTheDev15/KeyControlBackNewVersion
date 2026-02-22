pipeline {
    agent any

    stages {
        stage('Build e Deploy') {
            steps {
                sh 'docker compose up -d --build --no-deps api-backend'
            }
        }
    }
}