# Story 11.2: Embed Drift Report in Dashboard

As a MLOps Engineer,
I want to view the EvidentlyAI report directly within the dashboard,
So that I don't have to download HTML files manually.

## Acceptance Criteria

1. **[AC1]** The Streamlit app has a "Monitoring" or "Drift Report" tab.
2. **[AC2]** The app fetches the latest `latest_drift_report.html` from the S3 bucket (or local fallback).
3. **[AC3]** The HTML report is embedded directly into the Streamlit UI using `st.components.v1.html`.

## Tasks / Subtasks

- [ ] Task 1: S3 Integration in Dashboard
  - [ ] 1.1 Use `boto3` (via the existing `s3_client` utility) to download the latest drift report HTML string.
- [ ] Task 2: Streamlit Embedding
  - [ ] 2.1 Create a new tab in Streamlit and embed the HTML content securely.

## Status

**Status:** ready-for-dev
