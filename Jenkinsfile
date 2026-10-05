pipeline {
    agent any

    stages {
        stage('Build Backend Image') {
            steps {
                sh '''
                    cd backend
                    docker build -t abinayasenguttuvan/banking-backend:latest .
                '''
            }
        }

        stage('Build Frontend Image') {
            steps {
                sh '''
                    cd frontend
                    docker build -t abinayasenguttuvan/banking-frontend:latest .
                '''
            }
        }

        stage('Push Docker Images') {
            steps {
                sh '''
                    docker push abinayasenguttuvan/banking-backend:latest
                    docker push abinayasenguttuvan/banking-frontend:latest
                '''
            }
        }
    }
}
