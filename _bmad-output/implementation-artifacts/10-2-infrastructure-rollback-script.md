# Story 10.2: Infrastructure Rollback Script

As a MLOps Engineer,
I want a script or CI action to quickly revert to a previous state,
So that I can recover from a bad deployment in under 5 minutes.

## Acceptance Criteria

1. **[AC1]** A shell script or GitHub Action is provided to rollback to a specified Docker image tag.
2. **[AC2]** A script to fetch and load the previously registered stable model version from MLflow in case of model degradation.
3. **[AC3]** Documentation is provided in the repository on how to execute the rollback manually.

## Tasks / Subtasks

- [ ] Task 1: Rollback Scripts
  - [ ] 1.1 Create `scripts/rollback_container.sh` to pull and deploy a specified Docker tag.
  - [ ] 1.2 Create `scripts/rollback_model.py` to tag a previous MLflow model version as the 'Production' or stable alias, forcing the API to load the old version on restart.
- [ ] Task 2: Documentation
  - [ ] 2.1 Update `README.md` or a `docs/runbook.md` with instructions on using the rollback scripts.

## Status

**Status:** ready-for-dev
