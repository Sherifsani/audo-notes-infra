import boto3
import json
import uuid
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        bucket_name = f"upload-bucket-{uuid.uuid4()}"
        s3.create_bucket(Bucket=bucket_name)
        # Extract filename from query string or generate one
        filename = event.get("queryStringParameters", {}).get("filename")
        if not filename:
            filename = str(uuid.uuid4()) + ".jpg"  # Default to .jpg

        # Decode base64 image
        image_data = base64.b64decode(event['body'])

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
