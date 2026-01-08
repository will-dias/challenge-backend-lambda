import logging
import os

from bson.objectid import ObjectId
from pymongo import MongoClient

logger = logging.getLogger(__name__)

client = MongoClient(os.environ["MONGODB_URL"])
db = client[os.environ["DATABASE_NAME"]]


def get_catalog(owner_id: str):
    """Return the catalog tree for the provided owner identifier."""
    try:
        owner_object_id = ObjectId(owner_id)
    except Exception as exc:
        logger.error("Could not parse owner_id=%s into ObjectId: %s", owner_id, exc)
        return None

    pipeline = [
        {"$match": {"owner_id": owner_object_id}},
        {
            "$lookup": {
                "from": "product",
                "localField": "_id",
                "foreignField": "category",
                "as": "itens",
            }
        },
        {
            "$set": {
                "itens": {
                    "$map": {
                        "input": "$itens",
                        "as": "product",
                        "in": {
                            "title": "$$product.title",
                            "description": "$$product.description",
                            "price": "$$product.price",
                        },
                    }
                }
            }
        },
        {"$unset": ["_id", "owner_id"]},
        {
            "$project": {
                "category_title": "$title",
                "category_description": "$description",
                "itens": 1,
            }
        },
        {"$group": {"_id": None, "catalog": {"$push": "$$ROOT"}}},
        {"$replaceRoot": {"newRoot": {"catalog": "$catalog", "owner": owner_id}}},
    ]

    results = db.category.aggregate(pipeline)
    try:
        return results.next()
    except StopIteration:
        logger.info("No catalog found for owner_id=%s", owner_id)
        return None
