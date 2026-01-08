import importlib
import json
import os
from unittest.mock import MagicMock, patch

os.environ.setdefault("MONGODB_URL", "mongodb://example")
os.environ.setdefault("DATABASE_NAME", "test")

lambda_function = importlib.import_module("lambda_function")


def _make_record(message):
    return {"body": json.dumps({"Message": message})}


@patch("lambda_function.upload_catalog_s3")
@patch("lambda_function.get_catalog")
def test_process_record_uploads_catalog(get_catalog, upload_catalog_s3):
    get_catalog.return_value = {"catalog": "ok"}
    record = _make_record("owner-id")

    lambda_function.process_record(record)

    get_catalog.assert_called_once_with("owner-id")
    upload_catalog_s3.assert_called_once_with({"catalog": "ok"}, "owner-id")


@patch("lambda_function.upload_catalog_s3")
@patch("lambda_function.get_catalog", return_value=None)
def test_process_record_skips_without_catalog(get_catalog, upload_catalog_s3):
    lambda_function.process_record(_make_record("unknown"))

    upload_catalog_s3.assert_not_called()


@patch("lambda_function.process_record")
def test_lambda_handler_forwards_records(process_record):
    event = {"Records": [_make_record("1"), _make_record("2")]}

    lambda_function.lambda_handler(event, {})

    assert process_record.call_count == 2

