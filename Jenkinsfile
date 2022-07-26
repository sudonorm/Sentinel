pipeline{
    agent any
    
     triggers {
         cron('H/10 6-21 * * *') // Run script every 10 minutes
     }
    stages {
        //stage('Checkout Code') {
         //   steps {
          //      bat 'echo "code checked out" ' // this stage can be used to set-up some git checkout if "pipeline with SCM" is not selected while setting up the job
          //  }
       // }

        stage('Create VirtualEnv') {
            steps {
                bat 'python --version' // Add the Python path as a system environment variable to be able to use the Python installed on your Windows PC
                bat 'pip install virtualenv'
                bat 'virtualenv venv'
                bat 'python.exe -m pip install --upgrade pip'
                bat 'pip install -r requirements.txt' // Install requirements
                bat 'echo "set-up done" '
            }
        }

        stage('Get Listings') {
            steps {
                script {
                    
                    withCredentials([string(credentialsId: 'token_and_chat_id', variable: 'tokenChatId')]) {

                        bat 'echo Started...'
                        bat 'venv/Scripts/activate'
                        bat 'python get_listings.py -u %tokenChatId%' // run python script 
                        bat 'echo "Process complete!"'

                        }
                }
                
            }
        }
    }
 
    post {
        always {
                cleanWs() // clean up workspace
            }
	    }
}