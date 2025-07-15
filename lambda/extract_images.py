import boto3
import json
import urllib.parse as urlparse

textract = boto3.client("textract")
s3 = boto3.client("s3")

def lambda_handler(event, context):
    try:
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = urlparse.unquote_plus(record['s3']['object']['key'])

        response = textract.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            }
        )

        extracted_text = ""
        for block in response["Blocks"]:
            if block["BlockType"] == "LINE":
                extracted_text += block["Text"] + "\n"

        return {
            "statusCode": 200,
            "body": f"Text extracted from {key}:\n{extracted_text}"
        }

    except Exception as e:
        return {
            "status": 500,
            "message": json.dumps({
                "error": str(e),
                "bucket": bucket,
                "key": key
            })
        }