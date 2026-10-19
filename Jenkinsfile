
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
            python -m pip install --no-cache-dir --user -r requirements.txt
            python -m pytest -q
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
