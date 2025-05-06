pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    stages {

        stage('Cloning From GitHub.....') {
            steps {
                script {
                    echo 'Cloning From GitHub.....'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'GitHub_token_2', url: 'https://github.com/AhmadMajde22/Hybrid-Anime-Recommender-System.git']])
                }
            }
        }

        stage('Making Virtual Environment.....') {
            steps {
                script {
                    echo 'Making Virtual Environment.....'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    echo 'Virtual Environment setup complete.'
                    '''
                }
            }
        }

        stage('Apply Kubernetes Deployment') {
            steps {
                script {
                    echo 'Applying Kubernetes Deployment.....'
                    sh '''
                    kubectl apply -f deployment.yaml
                    echo "Waiting for the deployment to complete..."
                    kubectl rollout status deployment/dl-training-job --timeout=120s
                    echo "Deployment logs:"
                    kubectl logs deployment/dl-training-job
                    '''
                }
            }
        }
    }
}
