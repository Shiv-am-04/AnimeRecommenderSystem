pipeline{
    agent any

    stages{
        stage('Cloning github repo to jenkins'){
            steps{
                script{
                    echo 'cloning github repo to jenkins'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: '4', url: 'https://github.com/Shiv-am-04/AnimeRecommenderSystem.git']])
                }
            }
        }
    }
}