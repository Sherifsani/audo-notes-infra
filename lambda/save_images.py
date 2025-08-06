import os
import boto3
import json
import logging
import uuid
import re

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ['IMAGES_BUCKET']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Handle preflight OPTIONS request
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization"
                },
                "body": ""
            }

        # Handle POST request with JSON body
        if event.get("httpMethod") == "POST":
            # Parse the request body
            body = json.loads(event.get("body", "{}"))
            file_name = body.get("fileName")
            file_type = body.get("fileType")
        else:
            return {
                "statusCode": 405,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization"
                },
                "body": json.dumps({"message": "Method not allowed. Use POST."})
            }

        if not file_name or not file_type:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization"
                },
                "body": json.dumps({"message": "Missing fileName or fileType"})
            }

        # Validate file type is an image
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
        if file_type not in allowed_types:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization"
                },
                "body": json.dumps({"message": "Invalid file type. Only images are allowed."})
            }

        # Sanitize filename and add UUID to prevent conflicts
        # Remove any path separators and dangerous characters
        safe_filename = re.sub(r'[^\w\-_\.]', '', file_name)
        if not safe_filename:
            safe_filename = "image"
        
        # Add UUID prefix to prevent filename conflicts
        unique_filename = f"{uuid.uuid4()}_{safe_filename}"

        # Create pre-signed URL
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': unique_filename,
                'ContentType': file_type
            },
            ExpiresIn=300  # 5 minutes
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Consider restricting this to your domain
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,Authorization"
            },
            "body": json.dumps({
                "uploadUrl": presigned_url,
                "fileName": unique_filename
            })
        }

    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,Authorization"
            },
            "body": json.dumps({"message": "Internal server error", "error": str(e)})
        }
