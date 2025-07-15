import boto3
import json
import uuid
import base64
import urllib.parse

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        bucket_name = "images-bucket-1234"

        # Check if bucket exists
        try:
            s3.head_bucket(Bucket=bucket_name)
        except:
            s3.create_bucket(Bucket=bucket_name)

        # Get filename from query string or generate one
        query_params = event.get("queryStringParameters") or {}
        filename = query_params.get("filename")
        if not filename:
            filename = str(uuid.uuid4()) + ".jpg"

        # Decode the image
        if event.get("isBase64Encoded", False):
            # Binary body encoded by API Gateway
            image_data = base64.b64decode(event['body'])
        else:
            # Body is plain JSON with a base64 image field
            body_json = json.loads(event['body'])
            base64_str = body_json.get('image')
            if not base64_str:
                raise ValueError("No image data found in body")
            image_data = base64.b64decode(base64_str)
            filename = body_json.get('filename', filename)

        # Upload to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=image_data,
            ContentType="image/jpeg"
        )

        return {
            "statusCode": 200,
            "body": f"Image uploaded successfully as {filename}"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error uploading image: {str(e)}"
        }
