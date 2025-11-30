pipeline{
    agent any

    environment{
        VENV_DIR = '.venv'
        DOCKER_IMAGE = 'anime-recommender:latest'
        KIND_CLUSTER = 'anime-recommender'
    }

    stages{
        stage('Cloning github repo to jenkins'){
            steps{
                script{
                    echo 'cloning github repo to jenkins'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: '099aaacb-02d7-4ecb-a541-6e451fe2d953', url: 'https://github.com/Shiv-am-04/AnimeRecommenderSystem.git']])
                }
            }
        }

        stage('Creating Virtual Environment and Installing Dependencies'){
            steps{
                script{
                    echo 'setting up our venv and installing dependencies'
                    sh '''
                        python -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip
                        pip install -e .
                    '''
                }
            }
        }

        stage('DVC Pull') {
            steps {
                withCredentials([
                    string(credentialsId: 'AWS_ACCESS_KEY_ID', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'AWS_SECRET_ACCESS_KEY', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    script {
                        echo 'DVC Pull from S3...'
                        sh """
                            . ${VENV_DIR}/bin/activate

                            export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
                            export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
                            export AWS_DEFAULT_REGION=ap-south-1 

                            dvc pull
                        """
                    }
                }
            }
        }


        stage('Load Docker Image to Kind'){
            steps{
                script{
                    echo 'Loading Docker image to Kind cluster'
                    sh '''
                        # Create Kind cluster if it doesn't exist
                        if ! kind get clusters | grep -q ${KIND_CLUSTER}; then
                            kind create cluster --name ${KIND_CLUSTER}
                        fi
                        
                        # Load Docker image to Kind
                        kind load docker-image ${DOCKER_IMAGE} --name ${KIND_CLUSTER}
                    '''
                }
            }
        }

        stage('Deploy to Kind'){
            steps{
                script{
                    echo 'Deploying application to Kind cluster'
                    sh '''
                        # Set kubectl context to Kind cluster
                        kubectl cluster-info --context kind-${KIND_CLUSTER}
                        
                        # Apply Kubernetes manifests
                        kubectl apply -f k8s/namespace.yaml
                        kubectl apply -f k8s/deployment.yaml -n anime-recommender
                        
                        # Wait for deployment to be ready
                        kubectl wait --for=condition=available --timeout=300s deployment/anime-recommender -n anime-recommender
                        
                        # Get service info
                        kubectl get services -n anime-recommender
                    '''
                }
            }
        }

        stage('Verify Deployment'){
            steps{
                script{
                    echo 'Verifying deployment status'
                    sh '''
                        kubectl get pods -n anime-recommender
                        kubectl get services -n anime-recommender
                        
                        # Port forward for local access (optional)
                        echo "To access the application locally, run:"
                        echo "kubectl port-forward service/anime-recommender-service 8080:80 -n anime-recommender"
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed'
        }
        success {
            echo 'Deployment successful! Application is running on Kind cluster.'
        }
        failure {
            echo 'Deployment failed. Check logs for details.'
        }
    }
}