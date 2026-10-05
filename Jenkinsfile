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
                sh '''
                docker push abinayasenguttuvan/banking-frontend:latest
                docker push abinayasenguttuvan/banking-backend:latest
                '''
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
