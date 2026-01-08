# challenge-backend-lambda

Simple AWS Lambda consumer that reads catalog update messages from the `challenge-backend` producer service and stores the compiled catalog into S3.

## Setup

1. Create a virtual environment (e.g. `python -m venv env`) and activate it.
2. Install dependencies with `pip install -r requirements.txt`.
3. Bundle the `src/` directory and dependencies for deployment to Lambda. The handler is `src/lambda_function.lambda_handler`.

## Environment

The following environment variables configure this function:

- `MONGODB_URL` – connection string for the MongoDB cluster that stores categories/products.
- `DATABASE_NAME` – the database that contains the `category` and `product` collections.
- `CATALOG_BUCKET` – optional. Defaults to `catalog-marketplace-bucket-challenge`. The S3 bucket where catalog snapshots are saved.

## Integration

- This Lambda is triggered by the Kafka/SQS topic that `challenge-backend` publishes; each record must include a `Message` containing the MongoDB owner id.
- Validates and transforms the catalog for that owner, then uploads JSON to S3 using the `owner_id` as the key.

## Notes

- Logging is emitted via Python’s standard `logging` module for observability during batch processing.

