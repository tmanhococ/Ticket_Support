# Story 3.2: Create CI/CD Pipeline

Status: review

## Story

As a MLOps Engineer,
I want a GitHub Actions workflow that automatically runs tests, builds Docker images, pushes them to GHCR, and deploys to the EC2 Staging server,
So that every commit to `main` is automatically validated and deployed without any manual steps.

## Acceptance Criteria

1. **[AC1]** A GitHub Actions workflow file exists at `.github/workflows/ci-cd.yml`.
2. **[AC2]** The workflow triggers on: `push` to `main` branch, AND `pull_request` targeting `main`.
3. **[AC3]** **CI Job** runs in sequence:
   - Step 1: Lint with `flake8` (fails on errors — enforces code quality)
   - Step 2: Format check with `black --check .` (fails if unformatted)
   - Step 3: Run `pytest tests/ -v` (fails if any test fails)
4. **[AC4]** **Build & Push Job** (runs after CI job succeeds, only on `push` to `main`, not on PR):
   - Builds Docker image for `api` service with `docker build -t ghcr.io/{owner}/{repo}/tickets-api:{sha} .`
   - Tags image with both `{sha}` (short commit hash) and `latest`
   - Pushes both tags to **GitHub Container Registry (GHCR)**
5. **[AC5]** **Deploy Job** (runs after Build & Push job succeeds, only on `push` to `main`):
   - SSHs into the **Staging EC2** server using a stored GitHub Secret (`STAGING_SSH_KEY`, `STAGING_HOST`, `STAGING_USER`)
   - Pulls the new `latest` image from GHCR: `docker pull ghcr.io/{owner}/{repo}/tickets-api:latest`
   - Restarts the `api` container: `docker-compose up -d --no-deps api`
   - Executes a **Health Check gate**: `curl -f http://localhost:8000/health` — if it fails after 30s, the Deploy job fails.
6. **[AC6]** **Production Deploy** is triggered only on Git tag push matching `v*.*.*` (e.g., `v1.0.0`) — same steps as Staging Deploy but uses `PROD_SSH_KEY`, `PROD_HOST`, `PROD_USER` secrets.
7. **[AC7]** All sensitive values (SSH keys, EC2 host IPs, GHCR credentials) are stored as **GitHub Secrets** — never hardcoded in the workflow file.
8. **[AC8]** A `README.md` section documents how to set up the required GitHub Secrets and how to trigger a Production deploy via Git tag.
9. **[AC9]** The CI job passes locally (dry-run) by running `flake8 src/ tests/` and `black --check src/ tests/` and `pytest tests/ -v` — all should pass with the existing codebase (55 tests).

## Tasks / Subtasks

- [x] Task 1: Add linting/formatting dependencies to `requirements.txt` (AC: #3, #9)
  - [x] 1.1 Added `flake8==7.1.0` to `requirements.txt`
  - [x] 1.2 Added `black==24.4.2` to `requirements.txt`
  - [x] 1.3 Created `.flake8` config — max-line-length=100, excludes .git/__pycache__/.venv/build/dist/_bmad-output/.agent
  - [x] 1.4 Created `pyproject.toml` with `[tool.black]` section — line-length=100, target-version=py311
  - [x] 1.5 Ran `black src/ tests/` — 15 files reformatted, 7 unchanged
  - [x] 1.6 Ran `flake8 src/ tests/` → fixed 2 errors: E501 long line in run_simulator.py, F401 unused pytest import in conftest.py

- [x] Task 2: Create GitHub Actions CI/CD workflow (AC: #1, #2, #3, #4, #5, #6, #7)
  - [x] 2.1 Created `.github/workflows/ci-cd.yml`
  - [x] 2.2 Triggers: `push: branches: [main], tags: [v*.*.*]` + `pull_request: branches: [main]`
  - [x] 2.3 `ci` job: checkout → setup-python@v5 → pip install → flake8 → black --check → pytest
  - [x] 2.4 `build-and-push` job: GHCR login (GITHUB_TOKEN) → extract short SHA → docker/build-push-action@v5 (2 tags)
  - [x] 2.5 `deploy-staging` job: appleboy/ssh-action@v1.0.3 → docker pull → docker-compose up → retry health check loop (6×10s)
  - [x] 2.6 `deploy-production` job: same pattern, triggered by `refs/tags/v*`, uses PROD_* secrets

- [x] Task 3: Document GitHub Secrets setup in `README.md` (AC: #8)
  - [x] 3.1 Created full `README.md` with quickstart, CI/CD section, project structure, sprint roadmap
  - [x] 3.2 Documented all 6 required GitHub Secrets in a markdown table with descriptions
  - [x] 3.3 Documented EC2 one-time setup steps + Production deploy via `git tag v1.0.0 && git push origin v1.0.0`

- [x] Task 4: Local CI validation (AC: #9)
  - [x] 4.1 `flake8 src/ tests/` → **0 errors** ✅
  - [x] 4.2 `black --check src/ tests/` → **22 files would be left unchanged** ✅
  - [x] 4.3 `pytest tests/ -v` → **55 passed, 3 skipped, 0 failed** ✅

## Dev Notes

### GitHub Actions Workflow — Full Reference

```yaml
# .github/workflows/ci-cd.yml

name: CI/CD Pipeline

on:
  push:
    branches: [main]
    tags: ["v*.*.*"]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository_owner }}/tickets-api

jobs:
  # ============================================================
  # Job 1: CI — Lint, Format, Test
  # Runs on: all triggers (push, PR, tag)
  # ============================================================
  ci:
    name: Lint & Test
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Lint with flake8
        run: flake8 src/ tests/

      - name: Format check with black
        run: black --check src/ tests/

      - name: Run tests with pytest
        run: pytest tests/ -v
        env:
          # DATABASE_URL is not needed for unit tests (DB is mocked via conftest.py)
          DATABASE_URL: "postgresql+asyncpg://test:test@localhost/test"

  # ============================================================
  # Job 2: Build & Push Docker image to GHCR
  # Runs on: push to main only (not PRs)
  # ============================================================
  build-and-push:
    name: Build & Push Docker Image
    needs: ci
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract short SHA
        id: sha
        run: echo "short=${GITHUB_SHA::7}" >> $GITHUB_OUTPUT

      - name: Build and push API image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: src/api/Dockerfile
          push: true
          tags: |
            ghcr.io/${{ env.IMAGE_NAME }}:${{ steps.sha.outputs.short }}
            ghcr.io/${{ env.IMAGE_NAME }}:latest

  # ============================================================
  # Job 3: Deploy to Staging
  # Runs on: push to main, after successful build
  # ============================================================
  deploy-staging:
    name: Deploy to Staging
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: staging

    steps:
      - name: Deploy to Staging EC2 via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            # Pull latest image
            docker pull ghcr.io/${{ env.IMAGE_NAME }}:latest

            # Restart API service only (no downtime for DB)
            cd ~/Ticket_Support
            docker-compose up -d --no-deps --build api

            # Wait for container to be healthy
            sleep 15

            # Health check gate
            curl -f http://localhost:8000/health || (echo "Health check FAILED" && exit 1)
            echo "Staging deploy successful!"

  # ============================================================
  # Job 4: Deploy to Production (triggered by Git tag)
  # Runs on: push of a tag matching v*.*.*
  # ============================================================
  deploy-production:
    name: Deploy to Production
    needs: ci
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')
    environment: production

    steps:
      - name: Deploy to Production EC2 via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            # Pull latest image (tag releases use the same 'latest' image)
            docker pull ghcr.io/${{ env.IMAGE_NAME }}:latest

            # Restart API service
            cd ~/Ticket_Support
            docker-compose up -d --no-deps --build api

            # Wait and health check
            sleep 15
            curl -f http://localhost:8000/health || (echo "Health check FAILED" && exit 1)
            echo "Production deploy successful for tag ${{ github.ref_name }}!"
```

### Understanding the `GITHUB_TOKEN` for GHCR

The built-in `secrets.GITHUB_TOKEN` has **package write permissions** when you add:
```yaml
permissions:
  contents: read
  packages: write
```
This means **no additional secret** is needed to push to GHCR — GitHub handles auth automatically.

### EC2 Server Prerequisites

The CI/CD workflow assumes the Staging EC2 already has:
1. Docker and docker-compose installed
2. The project cloned to `~/Ticket_Support`
3. A `.env` file at `~/Ticket_Support/.env` with production values
4. The SSH key in `STAGING_SSH_KEY` authorized in `~/.ssh/authorized_keys`

**This setup is done manually ONCE** (out of scope for this story — document in README).

### Flake8 Configuration — Key Rules

The existing codebase uses:
- Long import chains in `conftest.py`
- `asyncio` patterns that may trigger `E712`
- Type hints that may trigger `E226`

Use `.flake8` with:
```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,.venv,venv,build,dist,_bmad-output,.github
extend-ignore = E203,W503,E501
```

Run `flake8 src/ tests/` first to see what needs fixing, then decide whether to add `extend-ignore` rules or fix the code.

### Black Formatting — Pre-flight Check

**CRITICAL**: Run `black src/ tests/` (auto-format) BEFORE adding `black --check` to CI. If you add `--check` first without reformatting, the very first CI run will fail on format errors.

```bash
# Step 1: Auto-format everything
black src/ tests/

# Step 2: Verify (this is what CI will run)
black --check src/ tests/
# Expected: All done! ✨ 🍰 ✨  N files would be left unchanged.

# Step 3: Re-run tests to verify formatting didn't break anything
pytest tests/ -v
```

### Release Gate Design

The health check gate in the Deploy job uses a simple `curl -f`:
```bash
curl -f http://localhost:8000/health
```
`-f` flag makes curl return exit code 22 on HTTP errors, which causes the GitHub Actions step to fail.

If the API is slow to start, use a retry loop:
```bash
for i in {1..5}; do
  curl -f http://localhost:8000/health && break
  echo "Attempt $i failed, waiting 10s..."
  sleep 10
done
```

### Previous Story Dependencies

From Story 3.1 (must complete first):
- `src/api/Dockerfile` — build context fixed to project root
- `docker-compose.yml` — `api` service has healthcheck
- `Makefile` — `make test` and `make build` targets

From Epic 1 & 2:
- `tests/` directory — 55 passing unit tests
- `src/api/` — FastAPI app with `/health` endpoint
- `requirements.txt` — at project root

### README.md Section Template

```markdown
## CI/CD Pipeline

This project uses GitHub Actions for fully automated CI/CD.

### Required GitHub Secrets

Navigate to: Repository → Settings → Secrets and variables → Actions → New repository secret

| Secret Name     | Description                        |
|-----------------|------------------------------------|
| `STAGING_SSH_KEY` | Private SSH key for Staging EC2  |
| `STAGING_HOST`  | Staging EC2 public IP or hostname  |
| `STAGING_USER`  | SSH user on Staging EC2 (e.g., `ubuntu`) |
| `PROD_SSH_KEY`  | Private SSH key for Production EC2 |
| `PROD_HOST`     | Production EC2 public IP or hostname |
| `PROD_USER`     | SSH user on Production EC2         |

### Triggering Deploys

**Staging deploy** (automatic): Push or merge to `main` branch.

**Production deploy** (manual trigger via Git tag):
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Pipeline Flow

```
push to main
    ↓
[CI] Lint → Format → Test
    ↓ (pass)
[Build & Push] docker build → push to GHCR
    ↓ (pass)
[Deploy Staging] SSH → docker pull → docker-compose up → health check
```
```

### Key Files to Create/Modify

| File | Action | Notes |
|------|--------|-------|
| `.github/workflows/ci-cd.yml` | NEW | Full CI/CD pipeline |
| `.flake8` | NEW | Flake8 config |
| `pyproject.toml` | NEW | Black config |
| `requirements.txt` | MODIFY | Add flake8, black |
| `README.md` | MODIFY | Add CI/CD setup section |
| `src/**/*.py`, `tests/**/*.py` | MODIFY | Auto-format with black |

### Scope Boundary — What NOT to do in this story

- **DO NOT** set up EC2 servers (done manually by engineer, out of scope)
- **DO NOT** add S3 upload steps to CI (Epic 5)
- **DO NOT** add model training to CI (Epic 6)
- **DO NOT** add Docker multi-stage builds or layer caching optimization (out of scope)
- **DO NOT** set up monitoring or alerting in GitHub Actions (out of scope)
- **DO NOT** add `docker scan` or security scanning (nice-to-have, out of scope)

### References

- [Source: epics.md - Epic 3, Story 3.2] — AC definition
- [Source: architecture.md §2.6] — GitHub Actions, GHCR, EC2 SSH deploy strategy
- [Source: 05_ci_cd_and_release_flow.md §2–4] — CI steps, CD steps, Staging/Production promote flow
- [Source: 04_environment_and_deployment.md §4] — EC2 t2.micro/t3.small, Ubuntu, Docker-compose
- [Source: Story 3.1 Dev Notes] — Dockerfile, Makefile, docker-compose.yml
- [GitHub Actions docs] — `docker/login-action@v3`, `docker/build-push-action@v5`, `appleboy/ssh-action@v1.0.3`
- [GHCR docs] — `ghcr.io/${{ github.repository_owner }}/image-name` naming convention

## Dev Agent Record

### Agent Model Used
Claude Sonnet 4.6 (Thinking) — bmad-dev-story workflow

### Debug Log References
- `pip install flake8==7.1.0 black==24.4.2` → installed successfully
- `black src/ tests/` → 15 files reformatted, 7 unchanged
- `flake8 src/ tests/` (first run) → 2 errors: E501 in run_simulator.py:167, F401 in conftest.py:5
- After fixes: `flake8 src/ tests/` → **0 errors** ✅
- `black --check src/ tests/` → **22 files would be left unchanged** ✅
- `pytest tests/ -v` → **55 passed, 3 skipped, 0 failed** ✅

### Completion Notes List
- ✅ AC1: `.github/workflows/ci-cd.yml` created.
- ✅ AC2: Triggers on `push: branches: [main]`, `push: tags: [v*.*.*]`, `pull_request: branches: [main]`.
- ✅ AC3: `ci` job runs flake8 → black --check → pytest in sequence. Fails fast on any error.
- ✅ AC4: `build-and-push` job uses `docker/build-push-action@v5` with `GITHUB_TOKEN` for GHCR auth. Tags: `{sha7}` + `latest`.
- ✅ AC5: `deploy-staging` uses `appleboy/ssh-action@v1.0.3`. Retry health-check loop (6 attempts × 10s = 60s max).
- ✅ AC6: `deploy-production` triggered by `refs/tags/v*` tag push. Uses separate PROD_* secrets.
- ✅ AC7: All SSH keys and host IPs use GitHub Secrets — zero hardcoded values in workflow YAML.
- ✅ AC8: `README.md` created with full CI/CD section, Secrets table, EC2 setup guide, production deploy instructions.
- ✅ AC9: Local dry-run: flake8=0 errors, black=22 unchanged, pytest=55 passed.
- **E501 fix**: Split long warning log string in `run_simulator.py:167` using implicit string concatenation.
- **F401 fix**: Removed unused `import pytest` from `conftest.py` — `pytest_asyncio` handles fixture registration.
- **Design decision**: Deploy uses retry loop (6×10s) instead of simple `sleep 15 && curl` — more reliable on slow cold-starts.
- **GITHUB_TOKEN scope**: Added `permissions: packages: write` on `build-and-push` job only — principle of least privilege.

### File List
- `requirements.txt` [MODIFIED — added flake8==7.1.0, black==24.4.2]
- `.flake8` [NEW — max-line-length=100, excludes non-source dirs]
- `pyproject.toml` [NEW — [tool.black] config]
- `.github/workflows/ci-cd.yml` [NEW — full CI/CD pipeline]
- `README.md` [NEW — project docs with CI/CD setup guide]
- `src/simulator/run_simulator.py` [MODIFIED — fix E501 long line at 167]
- `tests/conftest.py` [MODIFIED — remove unused pytest import (F401)]
- `src/api/database.py` [MODIFIED — black reformatted]
- `src/api/routes/health.py` [MODIFIED — black reformatted]
- `src/api/main.py` [MODIFIED — black reformatted]
- `tests/test_docker_integration.py` [MODIFIED — black reformatted]
- `src/api/models.py` [MODIFIED — black reformatted]
- `src/api/routes/tickets.py` [MODIFIED — black reformatted]
- `tests/test_health.py` [MODIFIED — black reformatted]
- `tests/test_drift.py` [MODIFIED — black reformatted]
- `src/api/schemas.py` [MODIFIED — black reformatted]
- `tests/test_generator.py` [MODIFIED — black reformatted]
- `tests/test_tickets.py` [MODIFIED — black reformatted]
- `tests/test_schemas.py` [MODIFIED — black reformatted]
- `src/simulator/generator.py` [MODIFIED — black reformatted]
