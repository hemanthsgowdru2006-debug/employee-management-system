# Employee Management System --- CI/CD with Jenkins and Docker

A Flask-based Employee Management System backed by PostgreSQL, with a
CI/CD pipeline that checks out source code from GitHub, runs automated
tests, builds a Docker image, and publishes versioned and `latest`
images to Docker Hub.

> **Current implementation:** Automated testing and image publishing are
> configured. Automatic deployment of the newly published image to a
> running production environment is not part of the current pipeline.

## Table of Contents

-   [Project Overview](#project-overview)
-   [Architecture and Workflow](#architecture-and-workflow)
-   [Technology Stack](#technology-stack)
-   [Project Structure](#project-structure)
-   [Prerequisites](#prerequisites)
-   [Run the Application Locally](#run-the-application-locally)
-   [Run Tests](#run-tests)
-   [Git and GitHub Commands](#git-and-github-commands)
-   [Jenkins Setup](#jenkins-setup)
-   [Docker Hub Setup](#docker-hub-setup)
-   [CI/CD Pipeline Stages](#cicd-pipeline-stages)
-   [Verify the Results](#verify-the-results)
-   [Demonstration and Submission
    Guide](#demonstration-and-submission-guide)
-   [Troubleshooting](#troubleshooting)
-   [Security Notes](#security-notes)
-   [Possible Enhancements](#possible-enhancements)

## Project Overview

This project demonstrates how to automate software validation and
container-image publishing for an employee management web application.

### Objectives

-   Maintain application source code in GitHub.
-   Package the Flask application and its dependencies into a Docker
    image.
-   Use PostgreSQL for application data.
-   Run automated Python tests in Jenkins.
-   Build a Docker image after tests pass.
-   Authenticate securely to Docker Hub using a Jenkins credential.
-   Publish both a build-number tag and the `latest` tag.

## Architecture and Workflow

``` mermaid
flowchart TD
    A[Developer updates code] --> B[GitHub repository]
    B --> C[Jenkins pipeline]
    C --> D[Checkout source]
    D --> E[Install Python dependencies]
    E --> F[Run pytest tests]
    F -->|Tests pass| G[Build Docker image]
    G --> H[Authenticate to Docker Hub]
    H --> I[Push versioned image]
    I --> J[Push latest image]
    F -->|Tests fail| K[Pipeline fails]
```

The current pipeline is started manually with **Build Now**, unless a
GitHub webhook or polling trigger has been configured separately.

## Technology Stack

  Technology           Purpose
  -------------------- ----------------------------------------------------
  Python               Application and test code
  Flask                Web application framework
  Flask-SQLAlchemy     ORM integration
  Flask-Login          Login/session management
  PostgreSQL           Relational database
  pytest               Automated testing
  Docker               Container image and runtime
  Docker Compose       Running application and database services together
  Jenkins              Pipeline orchestration
  Git and GitHub       Version control and source hosting
  Docker Hub           Container image registry
  `python:3.12-slim`   Python test agent/base image

## Project Structure

``` text
employee-management-system/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile
├── requirements.txt
├── .env.example
├── .gitignore
├── templates/
├── static/
└── tests/
    └── test_app.py
```

-   `app.py` --- Flask application entry point.
-   `Dockerfile` --- instructions for building the application image.
-   `docker-compose.yml` --- configuration for application and
    PostgreSQL services.
-   `Jenkinsfile` --- declarative CI/CD pipeline.
-   `requirements.txt` --- Python dependencies.
-   `.env.example` --- example environment-variable configuration. Keep
    actual local values in an ignored `.env` file.
-   `tests/test_app.py` --- automated tests.
-   `templates/` and `static/` --- web templates and static assets.

## Prerequisites

Install or configure:

1.  Git.
2.  Docker Desktop with Docker Compose.
3.  A GitHub repository containing the project.
4.  Jenkins with access to the Docker daemon.
5.  A Docker Hub account and repository.
6.  Jenkins credentials for GitHub access and Docker Hub publishing.

Check local tools:

``` bash
git --version
docker --version
docker compose version
docker info
```

> **Windows note:** Run Windows commands in PowerShell or Command Prompt
> as appropriate. Jenkins pipeline shell commands use `sh` because they
> run in Linux-based agents/containers.

## Run the Application Locally

Run these commands from the project root.

### 1. Configure environment variables

Copy `.env.example` to `.env` and edit the values for your local
environment.

PowerShell:

``` powershell
Copy-Item .env.example .env
```

Command Prompt:

``` bat
copy .env.example .env
```

Use the variable names expected by the application's configuration and
`docker-compose.yml`. Do not commit `.env`.

### 2. Build and start the services

``` bash
docker compose up --build -d
```

### 3. Check service status

``` bash
docker compose ps
```

### 4. View logs

``` bash
docker compose logs -f
```

To view only the application service, check its service name in
`docker compose ps`, then run:

``` bash
docker compose logs -f <app-service-name>
```

### 5. Open the application

Visit <http://localhost:5000>.

Log in with the administrator account configured for your environment.
Do not put credentials in this README.

### 6. Stop the services

``` bash
docker compose down
```

To also remove the Compose-managed database volume, only if you
intentionally want to delete its persisted data:

``` bash
docker compose down -v
```

**Warning:** `docker compose down -v` can permanently remove database
data stored in Compose-managed volumes.

## Run Tests

To run the tests locally, use a Python environment with the dependencies
installed:

``` bash
python -m pip install -r requirements.txt
python -m pytest -q
```

The current test suite contains five tests covering:

-   Health endpoint response.
-   Redirecting unauthenticated users from the dashboard.
-   Dashboard access for a logged-in administrator.
-   Adding an employee.
-   Rejecting an invalid login.

The successful Jenkins build recorded **5 passed**.

## Git and GitHub Commands

Run commands from the project root.

### 1. Check the working tree

``` bash
git status
```

### 2. Stage and commit changes

``` bash
git add .
git commit -m "Describe the change"
```

### 3. Push to the main branch

``` bash
git push origin main
```

### 4. Review recent commits

``` bash
git log --oneline -5
```

Jenkins checks out the repository's `main` branch:

<https://github.com/hemanthsgowdru2006-debug/employee-management-system>

The repository may be private, so viewers need appropriate GitHub
access.

## Jenkins Setup

### 1. Open Jenkins

Visit <http://localhost:8080> and sign in.

Check whether the Jenkins container is running with:

``` bash
docker ps
```

### 2. Check required plugins

The pipeline uses the relevant Jenkins plugins, including:

-   Pipeline
-   Git
-   Credentials Binding
-   Docker Pipeline

Plugin names and availability can vary by Jenkins version.

### 3. Add the GitHub credential

Navigate to:

**Manage Jenkins → Credentials → System → Global credentials
(unrestricted) → Add Credentials**

Configure:

-   Kind: **Username with password**
-   Username: your GitHub username
-   Password: a GitHub Personal Access Token with repository read access
-   ID: `github-employee-repo`
-   Description: `GitHub access for Employee Management System`

Never put the token in the `Jenkinsfile`, source code, README, or
console output.

### 4. Configure the pipeline job

Create a **Pipeline** job named:

``` text
Employee-Management-CI-CD
```

Configure:

-   Definition: **Pipeline script from SCM**
-   SCM: **Git**
-   Repository URL:
    `https://github.com/hemanthsgowdru2006-debug/employee-management-system.git`
-   Credentials: `github-employee-repo`
-   Branch specifier: `*/main`
-   Script path: `Jenkinsfile`

Save the job.

### 5. Configure Docker access

The configured Jenkins setup uses Docker CLI access and the host Docker
socket. Verify that Docker commands work from the Jenkins environment.

Access to the Docker socket gives powerful control over the Docker host.
Use this arrangement only with trusted pipeline code and a trusted
Jenkins instance.

## Docker Hub Setup

Docker Hub repository:

<https://hub.docker.com/r/hemanth05632/employee-management>

### 1. Create a Docker Hub access token

Open Docker Hub account settings and find **Personal access tokens**.
Generate a token with repository **Read & Write** permissions if
supported by your account settings.

If a token has been exposed in a screenshot, log, chat, or repository,
revoke it and generate a replacement.

### 2. Store the token in Jenkins

Navigate to:

**Manage Jenkins → Credentials → System → Global credentials
(unrestricted) → Add Credentials**

Enter:

  Field         Value
  ------------- -------------------------
  Kind          Username with password
  Username      `hemanth05632`
  Password      Docker Hub access token
  ID            `dockerhub-credentials`
  Description   Docker Hub publishing

The ID must exactly match the `Jenkinsfile`.

### 3. Image tags

Each successful pipeline run publishes:

``` text
hemanth05632/employee-management:<BUILD_NUMBER>
hemanth05632/employee-management:latest
```

For example, build #8 produced:

``` text
hemanth05632/employee-management:8
hemanth05632/employee-management:latest
```

## CI/CD Pipeline Stages

  ---------------------------------------------------------------------------------------------------
  Stage                   What it does                                        Expected evidence
  ----------------------- --------------------------------------------------- -----------------------
  Checkout                Retrieves source from GitHub                        Checkout completes

  Run Python Tests        Installs dependencies and runs                      `5 passed`
                          `python -m pytest -q`                               

  Build Docker Image      Builds                                              Image build succeeds
                          `hemanth05632/employee-management:<BUILD_NUMBER>`   

  Push Image to Docker    Logs in using Jenkins credentials, tags and pushes  Versioned and `latest`
  Hub                     the image                                           tags pushed
  ---------------------------------------------------------------------------------------------------

### Trigger a pipeline run

1.  Open Jenkins at <http://localhost:8080>.
2.  Select `Employee-Management-CI-CD`.
3.  Click **Build Now**.
4.  Open the new build number.
5.  Select **Console Output**.
6.  Inspect the result.

### What happens if a test fails?

The pipeline's shell script uses `set -e`, so a failing test command
causes the test stage to fail and normally stops the pipeline before the
image-build and publishing stages. Confirm the result in Console Output.

### Result of the recorded run

The recorded successful run was build **#8**:

-   All five automated tests passed.
-   The Docker image built successfully.
-   The versioned image was pushed to Docker Hub.
-   The `latest` image was pushed to Docker Hub.
-   Jenkins reported `Finished: SUCCESS`.

These results describe the recorded build. Run a new build to
demonstrate the process again.

## Verify the Results

### 1. Jenkins

Open the job and show the latest successful build and its Console
Output:

<http://localhost:8080>

### 2. Docker Hub

Verify the versioned tag and `latest` tag:

<https://hub.docker.com/r/hemanth05632/employee-management/tags>

### 3. Check local Docker images

``` bash
docker images
```

Look for `hemanth05632/employee-management` in the output.

### 4. Pull the published image

``` bash
docker pull hemanth05632/employee-management:latest
```

### 5. Run a standalone container (optional)

Only do this if port `5000` is free and the application does not require
runtime configuration that has not been supplied. A standalone container
may not have the database connection and environment variables required
by the app.

``` bash
docker run --rm -p 5000:5000 hemanth05632/employee-management:latest
```

For the complete application with PostgreSQL, use the Compose
configuration and its required environment variables.

## Demonstration and Submission Guide

A 7--10 minute demonstration can follow this sequence:

1.  **Application (1--2 minutes):** Open `http://localhost:5000`, log in
    with your configured administrator account, show the dashboard, and
    demonstrate an employee-management operation.
2.  **GitHub (1 minute):** Show the repository, `Jenkinsfile`,
    `Dockerfile`, and tests.
3.  **Jenkins (2--3 minutes):** Click **Build Now** and show the
    checkout, test, build, and push stages. Point out `5 passed` and
    `Finished: SUCCESS`.
4.  **Docker Hub (1 minute):** Show the build-number tag and `latest`
    tag.
5.  **Docker (1 minute):** Show running services in Docker Desktop or
    with `docker compose ps`, if they are running.
6.  **Conclusion:** Explain how automated tests and image publishing
    reduce repetitive manual work and make a consistent image available
    for deployment.

### Screenshots to include

-   Application dashboard.
-   GitHub repository and project files.
-   Jenkins pipeline/build status.
-   Console Output showing all five tests passing.
-   Console Output showing image push success.
-   Docker Hub tags page.
-   Docker Compose service status, if applicable.

### Suggested explanation for the evaluator

> This project uses GitHub for source control and Jenkins to orchestrate
> the pipeline. Jenkins checks out the code, installs Python
> dependencies, runs automated pytest tests, builds a Docker image, and
> publishes versioned and latest tags to Docker Hub. The successful
> recorded build passed all five tests and published both image tags.
> The current implementation automates testing, image building, and
> image publishing; deployment to a running production environment is a
> possible extension.

## Troubleshooting

### Jenkins cannot find a credential ID

Check that both credential IDs exist in a store available to the job:

-   `github-employee-repo`
-   `dockerhub-credentials`

Credential IDs are case-sensitive and must match the `Jenkinsfile`.

### Docker Hub login or push fails

-   Confirm the username is `hemanth05632`.
-   Confirm the Docker Hub token is valid and has repository write
    permission.
-   Confirm the repository exists and the account can publish to it.
-   Update the Jenkins credential rather than putting the token in
    pipeline source.
-   Review the failed stage in Console Output.

### Tests fail

Run locally:

``` bash
python -m pip install -r requirements.txt
python -m pytest -q
```

Read the failure before changing the code. If a test depends on
configuration or database state, ensure the test setup is configured
appropriately.

### The application does not open on port 5000

Check status and logs:

``` bash
docker compose ps
docker compose logs --tail=100
```

Confirm the host port is not already in use and that the application
container is healthy.

### Docker warns about the legacy builder

A warning that Docker's legacy builder is deprecated is not necessarily
a build failure. For future maintenance, consider configuring Docker
Buildx and BuildKit.

## Security Notes

-   Never commit `.env`, passwords, database credentials, GitHub tokens,
    or Docker Hub tokens.
-   Keep `.env` ignored by Git and commit only `.env.example` with
    placeholder values.
-   Revoke and replace any access token exposed in screenshots, logs,
    chat, or source control.
-   Store credentials in Jenkins Credentials and reference them by
    credential ID.
-   Avoid printing secrets in pipeline logs.
-   Limit access to Jenkins and its build logs.
-   A Jenkins container with access to `/var/run/docker.sock` can
    control the Docker daemon; treat pipeline changes and Jenkins access
    as privileged operations.
-   Do not publish real employee data in screenshots or demonstrations.

## Possible Enhancements

These are future enhancements, not claims about the current
implementation:

-   Configure a GitHub webhook or polling trigger so new commits start
    the pipeline automatically.
-   Add a deployment stage to deploy the validated image to a test or
    production environment.
-   Add image vulnerability scanning.
-   Add code-quality and coverage reports.
-   Use separate development, staging, and production environments.
-   Add deployment health checks and a rollback strategy.
-   Configure a Docker credential helper or approved alternative to
    reduce the risk of storing registry credentials in plaintext Docker
    configuration.

## Project Links

-   **GitHub repository:**
    <https://github.com/hemanthsgowdru2006-debug/employee-management-system>
-   **Docker Hub repository:**
    <https://hub.docker.com/r/hemanth05632/employee-management>
-   **Docker Hub tags:**
    <https://hub.docker.com/r/hemanth05632/employee-management/tags>
-   **Local Jenkins:** <http://localhost:8080>
-   **Local application:** <http://localhost:5000>

------------------------------------------------------------------------

**Project status:** Core CI/CD pipeline verified --- automated tests,
Docker image build, and Docker Hub publishing completed successfully in
Jenkins build #8.
