pipeline {
     agent {
    node {
      label 'agent-1'
    }
  }
    stages {
         stage('Setup Python Virtual Environment'){
            steps {
                sh '''
                    chmod +x envsetup.sh
                    ./envsetup.sh
                    '''
            }
        }
        stage('Setup Nginx'){
            steps {
                sh '''
                    chmod +x nginx.sh
                    ./nginx.sh
                    '''
            }
        }
    }
}
