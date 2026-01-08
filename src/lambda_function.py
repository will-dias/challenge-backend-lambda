import json
import logging

import boto3
from bson import json_util

from catalog import get_catalog
from config import BUCKET

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

def process_record(record):
    body = json.loads(record.get("body") or "{}")
    owner_id = body.get("Message")

    if not owner_id:
        logger.warning("Skipping record without owner Message")
        return

    catalog = get_catalog(owner_id)
    if not catalog:
        logger.info("No catalog returned for owner_id=%s", owner_id)
        return

    upload_catalog_s3(catalog, owner_id)

def upload_catalog_s3(catalog, owner_id):
    logger.info("Uploading catalog for owner=%s to bucket=%s", owner_id, BUCKET)

    s3_client.put_object(
        Bucket=BUCKET,
        Key=owner_id,
        Body=json_util.dumps(catalog),
        ContentType="application/json",
    )

def lambda_handler(event, context):
    records = event.get("Records", []) or []
    for record in records:
        try:
            process_record(record)
        except Exception:
            logger.exception("Failed to process record, see previous logs")