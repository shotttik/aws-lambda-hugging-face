import io
import json
import uuid
from pprint import pprint
from urllib.request import urlopen, Request
import boto3

API_TOKEN = "YOUR_API_TOKEN"

s3_client = boto3.client("s3")

API_URLS = {
     "resnet-50": "https://api-inference.huggingface.co/models/microsoft/resnet-50",
    "mit-b0": "https://api-inference.huggingface.co/models/nvidia/mit-b0",
    "detr-resnet-50": "https://api-inference.huggingface.co/models/facebook/detr-resnet-50",
    "yolos-tiny": "https://api-inference.huggingface.co/models/hustvl/yolos-tiny"
}

def query_image(api_url, content):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    http_request = Request(api_url, data=content, headers=headers)
    with urlopen(http_request) as response:
        result = response.read().decode()
    return result

def lambda_handler(event, _):
    pprint(event)
    for record in event.get("Records"):
        bucket = record.get("s3").get("bucket").get("name")
        key = record.get("s3").get("object").get("key")

        print("Bucket", bucket)
        print("Key", key)

        # Download file from bucket
        file = io.BytesIO()
        s3_client.download_fileobj(Bucket=bucket, Key=key, Fileobj=file)
        file.seek(0)
        f_content = file.read()
        # Send file to Huggingface API for each API URL
        for model_name, api_url in API_URLS.items():
            result = query_image(api_url, f_content)
            print(f"Result for {model_name}")

            # Upload result to bucket as unique json file
            result_key = model_name + "_" + key.replace(key.split(".")[-1], "json")
            file = io.BytesIO()
            file.write(result.encode("utf-8"))
            file.seek(0)
            s3_client.upload_fileobj(file, bucket, result_key)
    print("Done")
    return {"statusCode": 200, "body": json.dumps("Done!")}

  
