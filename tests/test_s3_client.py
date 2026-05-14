import os
import tempfile
from unittest.mock import patch

import boto3
from moto import mock_aws

# Import the module to be tested
from src.api.utils import s3_client

# Environment variables for testing
TEST_BUCKET = "test-bucket"


@mock_aws
def test_upload_and_download_file():
    # Setup mock S3 environment
    with patch.dict(
        os.environ,
        {
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_REGION": "us-east-1",
            "S3_BUCKET_NAME": TEST_BUCKET,
        },
    ):
        # Explicitly set mock client and create the test bucket
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=TEST_BUCKET)

        # Create a temporary file to upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
            tmp_file.write(b"Hello, world!")
            tmp_file_path = tmp_file.name

        try:
            # Test upload
            object_name = "test-object.txt"
            success_upload = s3_client.upload_file(tmp_file_path, object_name)
            assert success_upload is True

            # Verify it exists in mock S3
            response = conn.list_objects_v2(Bucket=TEST_BUCKET)
            assert "Contents" in response
            assert len(response["Contents"]) == 1
            assert response["Contents"][0]["Key"] == object_name

            # Test download
            download_path = tmp_file_path + ".downloaded"
            success_download = s3_client.download_file(object_name, download_path)
            assert success_download is True

            # Verify content
            with open(download_path, "rb") as f:
                content = f.read()
                assert content == b"Hello, world!"

            # Cleanup downloaded file
            os.remove(download_path)

        finally:
            # Cleanup initial temp file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)


@mock_aws
def test_upload_failure_handling():
    with patch.dict(
        os.environ,
        {
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_REGION": "us-east-1",
            "S3_BUCKET_NAME": "non-existent-bucket",
        },
    ):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test")
            tmp_file_path = tmp_file.name

        try:
            # Attempting to upload to a non-existent bucket should be caught gracefully
            # and return False
            success_upload = s3_client.upload_file(tmp_file_path, "test.txt")
            assert success_upload is False
        finally:
            os.remove(tmp_file_path)
