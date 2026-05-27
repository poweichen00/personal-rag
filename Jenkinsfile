// Personal RAG - CI/CD pipeline
// Flow: lint -> test (+coverage) -> SonarQube quality gate
//       -> build Docker image -> push to Nexus -> deploy to the Jetson edge.
//
// Prerequisites on the Jenkins host:
//   - Docker available to the agent
//   - sonar-scanner CLI + a configured SonarQube server named 'sonarqube'
//   - credentials: 'nexus' (username/password), 'dgx-ssh' (SSH key)
//   - the docker-compose.devops.yml stack running (Jenkins/SonarQube/Nexus)

pipeline {
  agent any

  environment {
    REGISTRY = 'localhost:8082'                 // Nexus hosted Docker registry port
    IMAGE    = "${REGISTRY}/personal-rag"
    TAG      = "${env.GIT_COMMIT?.take(7) ?: env.BUILD_NUMBER}"
  }

  options {
    timestamps()
    timeout(time: 30, unit: 'MINUTES')
  }

  parameters {
    // Off by default: the Jetson deploy needs the 'dgx-ssh' credential and a
    // reachable edge device. Tick it in "Build with Parameters" once ready.
    booleanParam(name: 'DEPLOY_TO_DGX', defaultValue: false,
                 description: 'Deploy the image to the Jetson edge device')
  }

  stages {
    stage('Setup') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install -q -r requirements-dev.txt
        '''
      }
    }

    stage('Lint') {
      steps {
        sh '. .venv/bin/activate && ruff check src tests'
      }
    }

    stage('Test') {
      steps {
        sh '''
          . .venv/bin/activate
          pytest -q --cov=src --cov-report=xml --junitxml=junit.xml
        '''
      }
      post {
        always { junit 'junit.xml' }
      }
    }

    stage('SonarQube') {
      steps {
        withSonarQubeEnv('sonarqube') {
          sh 'sonar-scanner'
        }
      }
    }

    stage('Quality Gate') {
      steps {
        timeout(time: 5, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
        }
      }
    }

    stage('Build image') {
      steps {
        sh "docker build -t ${IMAGE}:${TAG} -t ${IMAGE}:latest ."
      }
    }

    stage('Push to Nexus') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'nexus',
                          usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASS')]) {
          sh '''
            echo "$NEXUS_PASS" | docker login ${REGISTRY} -u "$NEXUS_USER" --password-stdin
            docker push ${IMAGE}:${TAG}
            docker push ${IMAGE}:latest
          '''
        }
      }
    }

    stage('Deploy to Jetson') {
      when { expression { params.DEPLOY_TO_DGX } }
      steps {
        sshagent(['dgx-ssh']) {
          sh '''
            ssh -o StrictHostKeyChecking=no nvidia@100.109.161.95 "
              docker pull ${IMAGE}:latest &&
              echo 'deployed ${IMAGE}:latest to Jetson edge'
            "
          '''
        }
      }
    }
  }

  post {
    always { cleanWs() }
  }
}
