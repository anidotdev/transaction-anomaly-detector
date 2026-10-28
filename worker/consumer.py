
import json
import os
import time

import boto3

from worker.model import load_model
from worker.predictor import process_transaction


STREAM_NAME = os.environ.get(
    "KINESIS_STREAM_NAME",
    "paysim-transactions",
)
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def main():
    kinesis = boto3.client("kinesis", region_name=AWS_REGION)
    model = load_model()

    response = kinesis.describe_stream(StreamName=STREAM_NAME)
    shards = response["StreamDescription"]["Shards"]

    if len(shards) != 1:
        raise RuntimeError(
            "This initial consumer supports one shard. "
            "Multi-shard support will be added later."
        )

    shard_id = shards[0]["ShardId"]

    iterator_response = kinesis.get_shard_iterator(
        StreamName=STREAM_NAME,
        ShardId=shard_id,
        ShardIteratorType="TRIM_HORIZON",
    )
    iterator = iterator_response["ShardIterator"]

    print(f"Consuming stream: {STREAM_NAME}")

    while iterator:
        response = kinesis.get_records(
            ShardIterator=iterator,
            Limit=100,
        )

        for record in response["Records"]:
            event = json.loads(record["Data"].decode("utf-8"))

            transaction_id = event["transaction_id"]
            transaction = event["transaction"]

            result = process_transaction(
                model=model,
                transaction_id=transaction_id,
                transaction=transaction,
            )

            print(json.dumps(result))

        iterator = response.get("NextShardIterator")
        time.sleep(1)


if __name__ == "__main__":
    main()
