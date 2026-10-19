pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'YOUR_DOCKERHUB_USERNAME/employee-management'
    }
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Install dependencies') {
            steps {
                sh 'python3 -m venv .venv'
                sh '.venv/bin/pip install --upgrade pip'
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }
        stage('Run tests') { steps { sh '.venv/bin/pytest -q' } }
        stage('Build Docker image') {
            steps { sh 'docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .' }
        }
        stage('Push image to Docker Hub') {
            when { branch 'main' }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_TOKEN')]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin
                        docker tag "$DOCKER_IMAGE:$BUILD_NUMBER" "$DOCKER_IMAGE:latest"
                        docker push "$DOCKER_IMAGE:$BUILD_NUMBER"
                        docker push "$DOCKER_IMAGE:latest"
                        docker logout
                    '''
                }
            }
        }
    }
    post { always { echo 'CI pipeline finished. Review stage results.' } }
}
