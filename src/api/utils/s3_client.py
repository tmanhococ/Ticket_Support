import os
import logging
import boto3

logger = logging.getLogger(__name__)


def get_s3_client():
    """Initialize and return a boto3 S3 client."""
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "ap-southeast-1")
    s3_bucket_name = os.getenv("S3_BUCKET_NAME")

    if not all([aws_access_key_id, aws_secret_access_key, s3_bucket_name]):
        logger.warning("AWS credentials or S3 bucket not fully configured in environment.")

    return boto3.client(
        "s3",
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )


def upload_file(file_path: str, object_name: str = None) -> bool:
    """
    Upload a file to an S3 bucket.

    :param file_path: File to upload
    :param object_name: S3 object name. If not specified, file_name is used
    :return: True if file was uploaded, else False
    """
    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_client = get_s3_client()

    try:
        if s3_bucket_name:
            s3_client.upload_file(file_path, s3_bucket_name, object_name)
            logger.info(
                "Successfully uploaded %s to s3://%s/%s", file_path, s3_bucket_name, object_name
            )
            return True
        else:
            logger.error("S3_BUCKET_NAME is not set, cannot upload %s", file_path)
            return False
    except Exception as e:
        logger.error("Failed to upload file to S3: %s", e)
        return False


def download_file(object_name: str, file_path: str) -> bool:
    """
    Download a file from an S3 bucket.

    :param object_name: S3 object name
    :param file_path: File path to save the downloaded file
    :return: True if file was downloaded, else False
    """
    s3_bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_client = get_s3_client()

    try:
        if s3_bucket_name:
            s3_client.download_file(s3_bucket_name, object_name, file_path)
            logger.info(
                "Successfully downloaded s3://%s/%s to %s", s3_bucket_name, object_name, file_path
            )
            return True
        else:
            logger.error("S3_BUCKET_NAME is not set, cannot download %s", object_name)
            return False
    except Exception as e:
        logger.error("Failed to download file from S3: %s", e)
        return False
