# Story 5.2: Configure AWS S3 Client

As a MLOps Engineer,
I want a utility to upload and download files from S3,
So that I can store models and reports externally.

## Acceptance Criteria

1. **[AC1]** An S3 client utility is created using `boto3`.
2. **[AC2]** The utility exposes methods/functions to upload files to and download files from a specified S3 bucket.
3. **[AC3]** AWS credentials and bucket names are read from environment variables and not hardcoded.
4. **[AC4]** AWS API exceptions (e.g., `ClientError`) are caught and handled gracefully.

## Tasks / Subtasks

- [x] Task 1: Implement S3 Utility Methods
  - [x] 1.1 Add `boto3` to `requirements.txt`.
  - [x] 1.2 Create `src/api/utils/s3_client.py`.
  - [x] 1.3 Implement `upload_file(file_path, object_name)` and `download_file(object_name, file_path)`.
- [x] Task 2: Setup Environment and Error Handling
  - [x] 2.1 Integrate environment variables for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, and `S3_BUCKET_NAME`.
  - [x] 2.2 Add `try-except` blocks for `ClientError` to ensure the application doesn't crash on S3 failures.
- [x] Task 3: Add Unit Tests
  - [x] 3.1 Add `moto` to testing dependencies.
  - [x] 3.2 Write a test suite to mock S3 upload and download operations, verifying the utility works correctly.

## Dev Notes

- **Business Context:** In preparation for model training (Epic 6) and Data Drift monitoring (Epic 9), the system needs a reliable, stateless way to store model artifacts and HTML reports. AWS S3 will be used as the blob storage.
- **Architecture Compliance:** Aligns with section 2.3 Storage decision to use AWS S3 for saving raw data, model artifacts, and reports.
- **Local Dev:** Provide documentation or mock setups on how developers can test locally without real AWS access if needed. 

## Dev Agent Record
- **Debug Log:** tests passed successfully. Fixed an issue with how `os.getenv` was evaluated inside `s3_client.py` during module load, ensuring tests can mock the variables successfully. Caught broad exceptions to handle Boto exceptions like `S3UploadFailedError`.
- **Completion Notes:** Story implemented completely. All ACs met. S3 client built, tested with `moto`, environment variables configured, tests passing.

## Change Log
- Added `boto3` and `moto` to `requirements.txt`.
- Created `src/api/utils/s3_client.py` with `upload_file` and `download_file`.
- Configured `.env.example`.
- Created `tests/test_s3_client.py` with mocking tests.
- Date: 2026-05-13/14

## Status

**Status:** review
