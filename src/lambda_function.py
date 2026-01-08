import json
import boto3
from bson import json_util

from src.catalog import get_catalog
from src.config import BUCKET

s3_client = boto3.client("s3")

def process_record(record):
    body = json.loads(record["body"])
    owner_id = body["Message"]

    catalog = get_catalog(owner_id)
    if not catalog:
        return

    upload_catalog_s3(catalog, owner_id)

def upload_catalog_s3(catalog, owner_id):

    s3_client.put_object(
        Bucket=BUCKET,
        Key=owner_id,
        Body=json_util.dumps(catalog),
        ContentType="application/json",
    )

def lambda_handler(event, context):
    for r in event["Records"]:
        process_record(r)