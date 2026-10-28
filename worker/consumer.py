
import json
import os
import time

import boto3

from worker.model import load_model
from worker.predictor import process_transaction

REGION = os.getenv("AWS_REGION", "us-east-1")
STREAM_NAME = os.getenv("KINESIS_STREAM_NAME", "paysim-transactions")


def main():
    kinesis = boto3.client("kinesis", region_name=REGION)
    model = load_model()

    stream = kinesis.describe_stream(StreamName=STREAM_NAME)
    shards = stream["StreamDescription"]["Shards"]

    if not shards:
        raise RuntimeError(f"No shards found in stream {STREAM_NAME}")

    iterators = {}

    for shard in shards:
        shard_id = shard["ShardId"]
        response = kinesis.get_shard_iterator(
            StreamName=STREAM_NAME,
            ShardId=shard_id,
            ShardIteratorType="TRIM_HORIZON",
        )
        iterators[shard_id] = response["ShardIterator"]

    print(f"Worker started. Consuming {len(iterators)} shard(s).")

    while iterators:
        for shard_id in list(iterators):
            response = kinesis.get_records(
                ShardIterator=iterators[shard_id],
                Limit=100,
            )

            for record in response["Records"]:
                try:
                    event = json.loads(record["Data"].decode("utf-8"))
                    result = process_transaction(
                        model,
                        event["transaction_id"],
                        event["transaction"],
                    )
                    print(json.dumps(result))
                except Exception as exc:
                    print(f"Failed to process record from {shard_id}: {exc}")

            next_iterator = response.get("NextShardIterator")
            if next_iterator:
                iterators[shard_id] = next_iterator
            else:
                del iterators[shard_id]

        time.sleep(1)


if __name__ == "__main__":
    main()
