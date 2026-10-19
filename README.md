# Employee Management System with CI/CD Automation

Flask employee management app with PostgreSQL, Docker, Docker Compose, pytest, and Jenkins.

## Features
- Admin login with hashed password storage
- Dashboard with employee/department counts
- Employee create, view, search, update, and delete
- Department create and delete
- PostgreSQL persistence using Docker Compose
- `/health` database health endpoint
- Automated pytest tests and Jenkins CI pipeline starter

## Run with Docker Desktop
1. Start Docker Desktop and wait for the engine to be running.
2. Copy `.env.example` to `.env`, then replace all example secrets with strong values.
3. In this folder, run:
   ```bash
   docker compose up --build -d
   ```
4. Open http://localhost:5000 and sign in with the values in `.env`.
5. Check http://localhost:5000/health.

Stop the containers but keep data: `docker compose down`
Delete containers and database data: `docker compose down -v` (destructive).

## Run locally on Windows
Python 3.12 is recommended. Python 3.14 may work, but if dependencies fail to install, use Python 3.12.
```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Without `DATABASE_URL`, local mode uses SQLite. The first run creates the database, an admin, and sample departments.
Demo credentials for local-only use: `admin` / `Admin123!`. Change these before sharing or deploying.

## Tests
```bash
python -m pytest -q
```
Tests use a temporary SQLite database and do not require PostgreSQL.

## GitHub
```bash
git init
git add .
git commit -m "Initial Employee Management System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/employee-management-system.git
git push -u origin main
```
Replace the URL with your repository. Never commit `.env`.

## Jenkins CI/CD setup
- Jenkins agent needs Git, Python 3, pip, Docker CLI, and permission to access the Docker daemon.
- Install Pipeline and Git plugins. Configure a Pipeline job from this repository and use the checked-in `Jenkinsfile`.
- Change `DOCKER_IMAGE` in `Jenkinsfile` to `YOUR_DOCKERHUB_USERNAME/employee-management`.
- Add a Jenkins username/password credential with ID `dockerhub-credentials`; use a Docker Hub access token as the password.
- Configure builds for `main`. GitHub webhooks need Jenkins to be reachable by GitHub; a local-only Jenkins server cannot receive public webhooks without a suitable tunnel or polling.
- The pipeline tests the code, builds the image, and pushes it from `main`. It does not yet deploy to a server: add a deployment stage only after you choose a target host and configure its credentials.

## Security and production notes
- Set strong `SECRET_KEY`, database password, and admin credentials.
- Use Jenkins Credentials or a secret manager for production secrets.
- Add CSRF protection and HTTPS before public deployment.
- `db.create_all()` is used for starter simplicity; use migrations for a maintained production system.
- Restrict Docker daemon access; access to it is highly privileged.
