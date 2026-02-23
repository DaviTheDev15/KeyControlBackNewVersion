pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "davithedev/backendkeycontrol"
        VERSION = "${BUILD_NUMBER}"
    }

    stages {

        stage('Build Image') {
            steps {
                sh "docker build -t $DOCKER_IMAGE:$VERSION ."
            }
        }

        stage('Login DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }

        stage('Push Image') {
            steps {
                sh "docker push $DOCKER_IMAGE:$VERSION"
                sh "docker tag $DOCKER_IMAGE:$VERSION $DOCKER_IMAGE:latest"
                sh "docker push $DOCKER_IMAGE:latest"
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker compose -f docker-compose.backend.yml down'
                sh 'docker compose -f docker-compose.backend.yml up -d'
            }
        }
    }
}