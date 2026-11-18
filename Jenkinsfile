pipeline {
    agent any
    options {
        timestamps()
        disableConcurrentBuilds()
    }
    triggers {
        githubPush()
    }
    environment {
        STUDENT_ID = 'FA23-BDS-064'
        SENDER     = 'naqiyaali123@gmail.com'
        IMAGE      = 'midterm-api'
    }
    stages {
        stage('Fetch Latest Data') {
            steps {
                sh '''
                    git log -1 --oneline
                    echo "Dataset lines (incl. header):"
                    wc -l dataset/train.csv
                '''
            }
        }
        stage('Train') {
            steps {
                sh 'docker build --progress=plain --target trained --build-arg GIT_COMMIT=${GIT_COMMIT} -t ${IMAGE}:trained .'
            }
        }
        stage('Test') {
            steps {
                sh 'docker build --progress=plain --target tested --build-arg GIT_COMMIT=${GIT_COMMIT} -t ${IMAGE}:tested .'
            }
        }
        stage('Build Image') {
            steps {
                sh 'docker build --build-arg GIT_COMMIT=${GIT_COMMIT} -t ${IMAGE}:latest .'
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f midterm-api || true
                    docker run -d --name midterm-api --restart unless-stopped -p 8000:8000 ${IMAGE}:latest
                    for i in $(seq 1 20); do
                        curl -sf http://localhost:8000/metrics && break
                        sleep 3
                    done
                    curl -sf http://localhost:8000/metrics
                '''
            }
        }
    }
    post {
        always {
            sh 'docker image prune -f || true'
            script {
                try {
                    mail to: 'qasimalik@gmail.com',
                         from: env.SENDER,
                         subject: "[${env.STUDENT_ID}] MIDTERM build #${env.BUILD_NUMBER}: ${currentBuild.currentResult}",
                         body: "Student Reg No: ${env.STUDENT_ID}\nResult: ${currentBuild.currentResult}\nCommit: ${env.GIT_COMMIT}\nBuild: ${env.BUILD_URL}\n"
                } catch (err) {
                    echo "Email failed: ${err}"
                }
            }
        }
    }
}
