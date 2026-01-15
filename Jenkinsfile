pipeline{
    agent any

    environment{
        VENV_DIR = '.venv'
        DOCKER_IMAGE = 'anime-recommender'
        KIND_CLUSTER = 'anime-recommender-cluster'
        NAMESPACE = 'anime-recommender'
        BUILD_VERSION = "v1"
        PREVIOUS_VERSION = ""
    }

    parameters {
        choice(
            name: 'ACTION',
            choices: ['deploy', 'rollback'],
            description: 'Choose action: deploy new version or rollback to previous'
        )
        string(
            name: 'ROLLBACK_VERSION',
            defaultValue: '',
            description: 'Version to rollback to (only for rollback action)'
        )
    }

    stages{
        stage('Cloning github repo to jenkins'){
            steps{
                script{
                    echo 'cloning github repo to jenkins'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'GITHUB_TOKEN', url: 'https://github.com/Shiv-am-04/AnimeRecommenderSystem.git']])
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
                            git checkout model-v1
                            dvc pull
                        """
                    }
                }
            }
        }

        stage('Build and Tag Docker Image'){
            when {
                expression { params.ACTION == 'deploy' }
            }
            steps{
                script{
                    echo "Building Docker image with version ${BUILD_VERSION}"
                    sh """
                        docker build -t ${DOCKER_IMAGE}:${BUILD_VERSION} .
                        docker tag ${DOCKER_IMAGE}:${BUILD_VERSION} ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        stage('Load Docker Image to Kind'){
            when {
                expression { params.ACTION == 'deploy' }
            }
            steps{
                script{
                    echo 'Creating Kind cluster and loading Docker image'
                    sh """
                        # Create Kind cluster with config if it doesn't exist
                        if ! kind get clusters | grep -q ${KIND_CLUSTER}; then
                            kind create cluster --config=kind/kind-config.yaml --name ${KIND_CLUSTER}
                        fi
                        
                        # Load Docker image to Kind
                        kind load docker-image ${DOCKER_IMAGE}:${BUILD_VERSION} --name ${KIND_CLUSTER}
                        kind load docker-image ${DOCKER_IMAGE}:latest --name ${KIND_CLUSTER}
                    """
                }
            }
        }

        stage('Deploy to Kind'){
            when {
                expression { params.ACTION == 'deploy' }
            }
            steps{
                script{
                    echo "Deploying version ${BUILD_VERSION} to Kind cluster"
                    sh """
                        # Set kubectl context to Kind cluster
                        kubectl cluster-info --context kind-${KIND_CLUSTER}
                        
                        # Store current version for potential rollback
                        CURRENT_VERSION=\$(kubectl get deployment anime-recommender -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null | cut -d':' -f2 || echo "none")
                        echo "Current version: \$CURRENT_VERSION" > previous_version.txt
                        
                        # Apply Kubernetes manifests
                        kubectl apply -f k8s/namespace.yaml
                        
                        # Update deployment with new image
                        sed "s|image: anime-recommender:0.1|image: ${DOCKER_IMAGE}:${BUILD_VERSION}|g" k8s/deployment.yaml | kubectl apply -f - -n ${NAMESPACE}
                        
                        # Wait for rollout to complete
                        kubectl rollout status deployment/anime-recommender -n ${NAMESPACE} --timeout=300s
                        
                        # Verify deployment health
                        kubectl wait --for=condition=available --timeout=60s deployment/anime-recommender -n ${NAMESPACE}
                    """
                }
            }
        }

        stage('Rollback'){
            when {
                expression { params.ACTION == 'rollback' }
            }
            steps{
                script{
                    def rollbackVersion = params.ROLLBACK_VERSION ?: 'previous'
                    echo "Rolling back to version: ${rollbackVersion}"
                    
                    sh """
                        # Set kubectl context
                        kubectl cluster-info --context kind-${KIND_CLUSTER}
                        
                        if [ "${rollbackVersion}" = "previous" ]; then
                            # Rollback to previous revision
                            kubectl rollout undo deployment/anime-recommender -n ${NAMESPACE}
                        else
                            # Rollback to specific version
                            kubectl set image deployment/anime-recommender anime-recommender=${DOCKER_IMAGE}:${rollbackVersion} -n ${NAMESPACE}
                        fi
                        
                        # Wait for rollback to complete
                        kubectl rollout status deployment/anime-recommender -n ${NAMESPACE} --timeout=300s
                        
                        # Verify rollback health
                        kubectl wait --for=condition=available --timeout=60s deployment/anime-recommender -n ${NAMESPACE}
                    """
                }
            }
        }

        stage('Verify Deployment'){
            steps{
                script{
                    echo 'Verifying deployment status'
                    sh """
                        kubectl get pods -n ${NAMESPACE}
                        kubectl get services -n ${NAMESPACE}
                        
                        # Health check
                        echo "Performing health checks..."
                        kubectl get pods -n ${NAMESPACE} -l app=anime-recommender -o jsonpath='{.items[*].status.phase}' | grep -q Running
                        
                        echo "Deployment verification completed successfully"
                        echo "To access the application locally, run:"
                        echo "kubectl port-forward service/anime-recommender-service 8080:80 -n ${NAMESPACE}"
                    """
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