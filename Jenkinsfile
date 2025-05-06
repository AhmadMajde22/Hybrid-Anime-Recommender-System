pipeline {
    agent any

    stages {
        stage('Cloning From GitHub.....'){
            steps {
                script {
                    echo 'Cloning From GitHub.....'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'GitHub_token_2', url: 'https://github.com/AhmadMajde22/Hybrid-Anime-Recommender-System.git']])

                }
            }
        }
    }
}
