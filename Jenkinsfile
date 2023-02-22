pipeline {
    agent {
        label "agent-deploy"
    }
 
    stages {
       
        stage('install-docker') {
            steps {
               
                sh 'echo agent | sudo -S chmod +x installdocker.sh'
                sh 'echo agent | sudo -S ./installdocker.sh'
                sh 'echo agent | sudo -S ansible-playbook playbook-dcompose.yml'

            }
        }
    }
} 

