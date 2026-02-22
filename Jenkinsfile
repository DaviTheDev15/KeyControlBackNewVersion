pipeline {
    agent any

    stages {
        stage('Build e Deploy') {
            steps {
                sh 'docker compose up -d --build --no-deps --force-recreate --remove-orphans api-backend'
            }
        }
    }
}