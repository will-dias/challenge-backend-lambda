import importlib
import os
from unittest.mock import MagicMock

from bson.objectid import ObjectId


def _reload_catalog(monkeypatch):
    os.environ.setdefault("MONGODB_URL", "mongodb://example:27017")
    os.environ.setdefault("DATABASE_NAME", "testdb")

    fake_category = MagicMock()

    fake_db = MagicMock()
    fake_db.category = fake_category

    fake_client = MagicMock()
    fake_client.__getitem__.return_value = fake_db

    mock_client = MagicMock(return_value=fake_client)
    monkeypatch.setattr("pymongo.MongoClient", mock_client)

    catalog_module = importlib.import_module("src.catalog")
    return importlib.reload(catalog_module), fake_category


def test_get_catalog_builds_pipeline(monkeypatch):
    catalog_module, fake_category = _reload_catalog(monkeypatch)
    aggregate_results = MagicMock()
    aggregate_results.next.return_value = {"catalog": "ok"}
    fake_category.aggregate.return_value = aggregate_results

    owner_id = "507f1f77bcf86cd799439011"
    result = catalog_module.get_catalog(owner_id)

    fake_category.aggregate.assert_called_once()
    pipeline = fake_category.aggregate.call_args[0][0]
    match_stage = pipeline[0]["$match"]["owner_id"]

    assert isinstance(match_stage, ObjectId)
    assert str(match_stage) == owner_id
    assert result == {"catalog": "ok"}

