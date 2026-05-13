# Ticket Support — MLOps Ticket Triage System

A production-grade MLOps pipeline for automated support ticket triage. Built with FastAPI, PostgreSQL, Streamlit, MLflow, and GitHub Actions CI/CD.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Pydantic |
| Database | PostgreSQL 15 (Docker) |
| Containerization | Docker + docker-compose |
| CI/CD | GitHub Actions + GHCR |
| Dashboard | Streamlit |
| ML Tracking | MLflow |
| Drift Detection | EvidentlyAI |

## Quick Start (Local Development)

```bash
# 1. Clone and set up environment
git clone https://github.com/tmanhococ/Ticket_Support.git
cd Ticket_Support
cp .env.example .env          # Edit .env with your values

# 2. Start all services
make up                       # or: docker-compose up -d

# 3. Verify API is running
curl http://localhost:8000/health
# Expected: {"status":"ok","db":"connected"}

# 4. Run unit tests
pytest tests/ -v              # 55 tests, all should pass
```

## Available Make Commands

```bash
make build    # Build Docker images
make up       # Start all services (detached)
make down     # Stop and remove containers
make logs     # Follow container logs
make test     # Run pytest inside the API container
make ps       # Show container status
make restart  # Restart all services
make help     # Show all available commands
```

## Running the Simulator

```bash
# Normal mode — 10 tickets at 2 req/s
python -m src.simulator.run_simulator --rate 2 --total 10

# Drift mode — biases German/Incident distribution
python -m src.simulator.run_simulator --drift

# Mixed mode — 20% invalid payloads to test rejection pipeline
python -m src.simulator.run_simulator --rate 5 --invalid-rate 0.2

# Against Docker API (internal network)
docker-compose run --rm simulator
```

## Project Structure

```
Ticket_Support/
├── .github/workflows/          # CI/CD pipelines
│   └── ci-cd.yml
├── src/
│   ├── api/                    # FastAPI service
│   │   ├── main.py
│   │   ├── schemas.py          # Pydantic data contracts
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── database.py         # Async DB engine
│   │   ├── routes/             # health.py, tickets.py
│   │   └── Dockerfile
│   ├── simulator/              # Stream Simulator
│   │   ├── generator.py        # Ticket generators (normal, drift, invalid)
│   │   ├── run_simulator.py    # CLI entrypoint
│   │   └── Dockerfile
│   └── drift_monitor/          # EvidentlyAI (Sprint 3)
├── tests/                      # Unit + integration tests
├── docker-compose.yml
├── requirements.txt
├── Makefile
└── .env.example
```

## CI/CD Pipeline

This project uses **GitHub Actions** for fully automated CI/CD. Every push to `main` triggers the full pipeline.

### Pipeline Flow

```
push to main
    ↓
[CI] flake8 lint → black format check → pytest
    ↓ (all pass)
[Build & Push] docker build → push to GHCR (ghcr.io/tmanhococ/tickets-api)
    ↓ (success)
[Deploy Staging] SSH → docker pull → docker-compose up → health check gate

push tag v1.x.x
    ↓
[CI] (same as above)
    ↓ (all pass)
[Deploy Production] SSH → docker pull → docker-compose up → health check gate
```

### Required GitHub Secrets

Navigate to: **Repository → Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Description |
|-------------|-------------|
| `STAGING_SSH_KEY` | Private SSH key for Staging EC2 (PEM format, full contents) |
| `STAGING_HOST` | Staging EC2 public IP or hostname |
| `STAGING_USER` | SSH username on Staging EC2 (typically `ubuntu`) |
| `PROD_SSH_KEY` | Private SSH key for Production EC2 |
| `PROD_HOST` | Production EC2 public IP or hostname |
| `PROD_USER` | SSH username on Production EC2 |

> **Note:** `GITHUB_TOKEN` is built-in — no extra secret needed for GHCR image push.

### EC2 Server Prerequisites (One-Time Setup)

Before the first automated deploy, set up each EC2 server manually:

```bash
# 1. Install Docker and docker-compose
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker ubuntu

# 2. Clone the repository
cd ~
git clone https://github.com/tmanhococ/Ticket_Support.git

# 3. Create production .env file
cd ~/Ticket_Support
cp .env.example .env
nano .env  # Set real POSTGRES_PASSWORD etc.

# 4. Start the initial stack
docker-compose up -d db  # Start DB first
docker-compose up -d api  # Then API

# 5. Authorize the deploy SSH key
echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys
```

### Triggering Deploys

**Staging deploy** — automatic on every push to `main`:
```bash
git push origin main
```

**Production deploy** — triggered by creating a Git tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Local CI Dry-Run (verify before pushing)

```bash
# Run all CI checks locally
flake8 src/ tests/          # Must exit 0
black --check src/ tests/   # Must report "N files would be left unchanged"
pytest tests/ -v            # Must show 55 passed (+ 3 skipped Docker tests)
```

## Environment Variables

See [.env.example](.env.example) for a documented list of all required variables.

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | `tickets_user` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `tickets_pass` |
| `POSTGRES_DB` | Database name | `tickets_db` |
| `DATABASE_URL` | Full async DB connection string | see .env.example |
| `API_URL` | Simulator target URL (Docker internal) | `http://api:8000` |

## Sprint Roadmap

| Sprint | Focus | Status |
|--------|-------|--------|
| Sprint 1 | Foundation: API, Simulator, Docker, CI/CD, Dashboard skeleton | 🟡 In Progress |
| Sprint 2 | Model: Baseline training, MLflow, Shadow inference | ⬜ Backlog |
| Sprint 3 | Monitoring: Drift detection, Rollback, Dashboard polish | ⬜ Backlog |
