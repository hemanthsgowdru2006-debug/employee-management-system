
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'hemanth05632/employee-management'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run Python Tests') {
            agent {
                docker {
                    image 'python:3.12-slim'
                    reuseNode true
                    args '-e HOME=/tmp'
                }
            }
            steps {
                sh '''
                    set -e

                    echo "Installing Python dependencies..."
                    python -m pip install \
                        --no-cache-dir \
                        --user \
                        -r requirements.txt

                    echo "Running automated tests..."
                    python -m pytest -q
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e

                    echo "Building Employee Management Docker image..."

                    docker build \
                        -t "$DOCKER_IMAGE:$BUILD_NUMBER" \
                        .

                    echo "Docker image built successfully."
                '''
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        set -e

                        echo "Logging in to Docker Hub..."

                        echo "$DOCKERHUB_TOKEN" | docker login \
                            -u "$DOCKERHUB_USER" \
                            --password-stdin

                        echo "Tagging Docker images..."

                        docker tag \
                            "$DOCKER_IMAGE:$BUILD_NUMBER" \
                            "$DOCKER_IMAGE:latest"

                        echo "Pushing versioned image..."

                        docker push "$DOCKER_IMAGE:$BUILD_NUMBER"

                        echo "Pushing latest image..."

                        docker push "$DOCKER_IMAGE:latest"

                        docker logout

                        echo "Docker images pushed successfully."
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Tests passed, Docker image built, and image push completed.'
        }

        failure {
            echo 'FAILURE: A pipeline stage failed. Check Console Output for details.'
        }

        always {
            echo 'Employee Management System CI/CD pipeline execution completed.'
        }
    }
}
