# Dockerizing, Running Locally, Pushing to Docker Hub, and Deploying on AWS EC2

This guide shows, step-by-step, how to:
- Build a Docker image (without baking in your `.env`).
- Run the container locally while passing env variables at runtime.
- Push the image to Docker Hub.
- Create an EC2 instance, SSH in, create a `.env` on the VM, and run the container there.

The FastAPI app already supports environment variables and excludes `.env` from the image via `.dockerignore`.

---

## Prerequisites
- Windows with Docker Desktop installed (PowerShell).
- Docker Hub account (for pushing images).
- AWS account (EC2) with permissions to create instances and security groups.
- Your API key(s) handy (e.g., `GOOGLE_API_KEY`).

Environment variables used by this app:
- Required: `GOOGLE_API_KEY`
- Optional: `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`

See `.env.example` for reference.

---

## Project Expectations
- Build context is the `fastapi_app/` folder.
- The image packages `properties_sql.db` and `faiss_realestate_index/` (both are in this folder).
- `.dockerignore` prevents `.env` and other local files from being copied into the image.

---

## 1) Build the image (without `.env`)

From the `fastapi_app/` folder:

```powershell
docker build -t realestate-fastapi:latest .
```

Notes:
- If you change code, rebuild the image.
- If you change dependencies, ensure `requirements.txt` is updated before rebuilding.

---

## 2) Run locally (pass env at runtime)

Choose one of the following:

### Option A: Pass env variables inline (PowerShell)
```powershell
docker run --rm -p 8000:8000 `
   -e GOOGLE_API_KEY="<your_google_api_key>" `
   -e LANGSMITH_API_KEY="<optional>" `
   -e LANGSMITH_PROJECT="real-estate-rag" `
   realestate-fastapi:latest
```

### Option B: Use an env file (recommended for local)
```powershell
# Make sure you have a local .env in fastapi_app/ (NOT committed)
docker run --rm -p 8000:8000 --env-file .env realestate-fastapi:latest
```

Then visit: http://localhost:8000/docs

---

## 3) Tag and push to Docker Hub

Replace `DOCKERHUB_USER` with your Docker Hub username.

```powershell
docker tag realestate-fastapi:latest DOCKERHUB_USER/realestate-fastapi:latest
docker login
docker push DOCKERHUB_USER/realestate-fastapi:latest
```

Use semantic tags for versions if you prefer (e.g., `:v1`, `:2026-01-12`).

---

## 4) Deploy on AWS EC2

### 4.1 Create an EC2 instance
- AMI: Ubuntu 22.04 LTS (or Amazon Linux 2023)
- Instance type: `t2.micro` (free tier eligible)
- Security group inbound rules:
   - Allow `HTTP` TCP `80` from `0.0.0.0/0` (or restrict to your IP).
   - Allow `SSH` TCP `22` from your IP.

### 4.2 SSH into the instance
```bash
ssh -i /path/to/key.pem ubuntu@<EC2_PUBLIC_IP>
```

### 4.3 Install Docker (Ubuntu)
```bash
sudo apt-get update -y
sudo apt-get install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
# log out and log back in for group change to take effect
```

### 4.4 Pull your image from Docker Hub
```bash
docker login
docker pull DOCKERHUB_USER/realestate-fastapi:latest
```

### 4.5 Create `.env` on the server (do NOT commit this)
```bash
nano .env
```
Example contents:
```
GOOGLE_API_KEY=your_google_api_key_here
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=real-estate-rag
```
Save and exit (Ctrl+O, Enter, Ctrl+X).

### 4.6 Run the container with the env file
```bash
docker run -d --name realestate-api \
   -p 80:8000 \
   --env-file .env \
   DOCKERHUB_USER/realestate-fastapi:latest
```

Now open: `http://<EC2_PUBLIC_IP>/docs`

Optional: Restart policy so it survives reboots:
```bash
docker rm -f realestate-api || true
docker run -d --name realestate-api \
   --restart unless-stopped \
   -p 80:8000 \
   --env-file .env \
   DOCKERHUB_USER/realestate-fastapi:latest
```

---

## Troubleshooting
- 403 / 5xx from the API: Ensure `GOOGLE_API_KEY` is valid and has access to Gemini models.
- Container starts then exits: Check logs with `docker logs realestate-api`.
- 404 on `/docs`: Verify port mapping and security group rules.
- Missing FAISS/DB: Ensure `faiss_realestate_index/` and `properties_sql.db` exist in `fastapi_app/` before building.

---

## What changed or is required in the FastAPI project?
- Environment handling is already container-friendly:
   - The app reads `GOOGLE_API_KEY` (required) and `LANGSMITH_API_KEY` (optional) from environment variables.
   - `.dockerignore` excludes `.env` so secrets are not baked into the image.
   - `.env.example` documents required/optional variables.
- No code changes are required to run in Docker or on EC2.
- Recommended (optional) improvements:
   - Use `--env-file` or a secrets manager in production rather than inline `-e`.
   - Add a healthcheck to the Dockerfile if you want automated health monitoring.
   - Consider pinning dependency versions in `requirements.txt` for reproducible builds.

---

## Quick Command Reference (Windows PowerShell)
```powershell
# Build
docker build -t realestate-fastapi:latest .

# Run with inline envs
docker run --rm -p 8000:8000 -e GOOGLE_API_KEY="<key>" realestate-fastapi:latest

# Run with env file
docker run --rm -p 8000:8000 --env-file .env realestate-fastapi:latest

# Tag + Push
docker tag realestate-fastapi:latest DOCKERHUB_USER/realestate-fastapi:latest
docker login
docker push DOCKERHUB_USER/realestate-fastapi:latest
```

You’re set: build locally, test with envs at runtime, push to Docker Hub, and run on EC2 with a server-side `.env`. 🎉
