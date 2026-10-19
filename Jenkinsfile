
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
                echo "$DOCKERHUB_TOKEN" | docker login \
                    -u "$DOCKERHUB_USER" --password-stdin

                docker tag "$DOCKER_IMAGE:$BUILD_NUMBER" \
                    "$DOCKER_IMAGE:latest"

                docker push "$DOCKER_IMAGE:$BUILD_NUMBER"
                docker push "$DOCKER_IMAGE:latest"

                docker logout
            '''
        }
    }
}
