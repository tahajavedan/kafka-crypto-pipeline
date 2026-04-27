import json
import time
from kafka import KafkaConsumer
import boto3
from io import StringIO
from datetime import datetime
import logging

# ---------- CONFIG ----------
bucket = "my-crypto"
consumer = KafkaConsumer(
    "crypto.prices",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="crypto-group"
)

# MinIO client (boto3)
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin123"
)


def extract_upload_s3():
    print("\n" + "="*60)
    print("   LIVE CRYPTO STREAM")
    print("="*60)

    try:
        crypto_messages = []
        

        for cdata in consumer:
            data = json.loads(cdata.value.decode("utf-8"))
            
            
            print(f"{data['Coin_Name']:<12} | Price: {data['Current_Price']:<10} | High: {data['High_24h']} | Low: {data['Low_24h']}")
            crypto_messages.append(data)

            # print every 30 seconds the current length
      

            if len(crypto_messages) >= 10:
                # Build JSON array
                mem = StringIO()
                mem.write(json.dumps(crypto_messages, indent=4))
                mem.seek(0)

                # Create S3/MinIO key (UTC timestamp)
                key = f"Staging/crypto_messages_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

                # Upload
                s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=mem.getvalue()
                )
                print("\n" + "-"*60)
                print("Batch Uploaded to MinIO")
                print("-"*60 + "\n")
                print() 
                print("Uploaded:", key)
                print() 

                # Commit Kafka offsets
                consumer.commit()

                # Clear batch
                crypto_messages = []

    except Exception as e:
        logging.exception(f"Upload failed: {e}")


# Execute function

extract_upload_s3()
