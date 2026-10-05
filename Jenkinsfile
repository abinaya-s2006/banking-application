pipeline {
    agent any

    stages {

        stage('Build Frontend') {
            steps {
                sh '''
                cd frontend
                docker build -t abinayasenguttuvan/banking-frontend:latest .
                '''
            }
        }

        stage('Build Backend') {
            steps {
                sh '''
                cd backend
                docker build -t abinayasenguttuvan/banking-backend:latest .
                '''
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker_creds',
                    usernameVariable: 'abinayasenguttuvan',
                    passwordVariable: 'abinaya2328'
                )]) {
                    sh '''
                    echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                    docker push abinayasenguttuvan/banking-frontend:latest
                    docker push abinayasenguttuvan/banking-backend:latest
                    docker logout
                    '''
                }
            }
        }

        stage('Deploy Kubernetes') {
            steps {
                sh '''
                kubectl apply -f k8s
                '''
            }
        }
    }
}
