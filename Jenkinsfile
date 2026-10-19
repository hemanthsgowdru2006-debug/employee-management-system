
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'YOUR_DOCKERHUB_USERNAME/employee-management'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run Python Tests') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE:/app" \
                      -w /app \
                      python:3.12-slim \
                      sh -c "pip install --no-cache-dir -r requirements.txt pytest && pytest -q"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .'
            }
        }

        stage('Push Image to Docker Hub') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login \
                          -u "$DOCKERHUB_USER" --password-stdin

                        docker tag "$DOCKER_IMAGE:$BUILD_NUMBER" "$DOCKER_IMAGE:latest"
                        docker push "$DOCKER_IMAGE:$BUILD_NUMBER"
                        docker push "$DOCKER_IMAGE:latest"

                        docker logout
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'CI pipeline finished. Review stage results.'
        }
    }
}
