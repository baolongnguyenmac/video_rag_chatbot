// pipeline {
//     agent any

//     options{
//         // Enable timestamp at each job in the pipeline
//         timestamps()
//     }

//     environment {
//         IMG_NAME = 'baolongnguyenmac/chatbot_video_rag'
//         CTN_NAME = 'ctn_video_chatbot'
//     }

//     stages {
//         stage('test') {
//             agent {
//                 docker {
//                     image 'python:3.11-slim'
//                     args '--user root'  // run with root user
//                     reuseNode true
//                 }
//             }

//             steps {
//                 sh '''
//                     echo 'Preparing environment...'

//                     apt-get update && apt-get install -y curl
//                     curl -LsSf https://astral.sh/uv/install.sh | sh
//                     export PATH="$HOME/.local/bin:$PATH"

//                     uv pip compile requirements.in -o requirements.txt && \
//                     uv pip install \
//                         --extra-index-url https://download.pytorch.org/whl/cpu \
//                         --no-cache-dir --upgrade \
//                         --system \
//                         -r requirements.txt

//                     echo 'Testing...'

//                     pytest -v
//                 '''
//             }
//         }

//         stage('build') {
//             // when {
//             //     branch 'main'
//             // }

//             steps {
//                 sh '''
//                     echo 'Building docker image...'
//                     docker build -t ${IMG_NAME}:${BUILD_NUMBER} .
//                 '''
//             }
//         }

//         stage('deploy') {
//             // when {
//             //     branch 'main'
//             // }

//             steps {
//                 echo 'Deploying...'

//                 // push to DockerHub
//                 withCredentials([usernamePassword(
//                     credentialsId: '14950eb9-65e6-46de-b383-9a2dcb3577be',
//                     usernameVariable: 'USER',
//                     passwordVariable: 'PASS'
//                 )]) {
//                     sh '''
//                         # Login
//                         echo ${PASS} | docker login -u ${USER} --password-stdin

//                         echo 'Pushing image to DockerHub...'
//                         docker push ${IMG_NAME}:${BUILD_NUMBER}

//                         # Logout
//                         docker logout
//                     '''
//                 }

//                 // push to HuggingFace
//                 // ...

//                 // start container
//                 withCredentials([
//                     file(credentialsId: '919d33df-1ba7-4e6f-aabc-d8d118310f1e', variable: 'ENV_FILE')
//                 ]) {
//                     sh '''
//                         # change the tag of the newest docker img
//                         docker tag ${IMG_NAME}:${BUILD_NUMBER} ${IMG_NAME}:latest

//                         cp ${ENV_FILE} .env
//                         chmod 600 .env
//                         docker rm -f ${CTN_NAME}
//                         docker compose -f compose.yml up -d
//                     '''
//                 }
//             }

//             post {
//                 success {
//                     sh '''
//                         docker rmi ${IMG_NAME}:${BUILD_NUMBER}
//                     '''
//                 }
//             }
//         }
//     }
// }
