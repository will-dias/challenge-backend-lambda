from bson.objectid import ObjectId
from pymongo import MongoClient
import os

client = MongoClient(os.environ["MONGODB_URL"])
db = client[os.environ["DATABASE_NAME"]]


def get_catalog(owner_id: ObjectId):
    pipeline = [
        {"$match": {"owner_id": ObjectId(owner_id)}},
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
    return results.next()
