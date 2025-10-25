pipeline{
    agent any

    environment{
        VENV_DIR = '.venv'
    }

    stages{
        stage('Cloning github repo to jenkins'){
            steps{
                script{
                    echo 'cloning github repo to jenkins'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: '4', url: 'https://github.com/Shiv-am-04/AnimeRecommenderSystem.git']])
                }
            }
        }

        // stage('Creating Virtual Environment and Installing Dependencies'){
        //     steps{
        //         script{
        //             echo 'setting up our venv and installing dependencies'
        //             sh '''
        //                 python -m venv ${VENV_DIR}
        //                 . ${VENV_DIR}/bin/activate
        //                 pip install --upgrade pip
        //                 pip install -e .
        //             '''
        //         }
        //     }
        // }
        
        // stage('DVC Pull'){
        //     steps{
        //         withCredentials([file(credentialsId:'gcp-key',variable:'GOOGLE_APPLICATION_CREDENTIALS')]){
        //             echo 'DVC Pull...',
        //             sh '''
        //             . ${VENV_DIR}/bin/activate
        //             dvc pull
        //             '''
        //         }
        //     }
        // }
    }
}