import json
import boto3
import datetime
import base64
import uuid
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    s3 = boto3.client('s3')
    try:
        bucket_name = f'upload-bucket-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")}'
        logger.info(f"Target bucket: {bucket_name}")

        existing_buckets = s3.list_buckets()
        if not any(b['Name'] == bucket_name for b in existing_buckets['Buckets']):
            # For us-east-1, don't specify LocationConstraint
            s3.create_bucket(Bucket=bucket_name)
            logger.info(f"Created bucket: {bucket_name}")
        else:
            logger.info(f"Bucket already exists: {bucket_name}")

        body = event["body"]
        is_base64 = event.get("isBase64Encoded", False)

        if is_base64:
            image_bytes = base64.b64decode(body)
        else:
            # Handle both JSON payload and direct binary upload
            if isinstance(body, str):
                try:
                    # Try to parse as JSON first (for structured requests)
                    json_body = json.loads(body)
                    if "body" in json_body:
                        actual_body = json_body["body"]
                        actual_is_base64 = json_body.get("isBase64Encoded", False)
                        if actual_is_base64:
                            image_bytes = base64.b64decode(actual_body)
                        else:
                            image_bytes = actual_body.encode("utf-8")
                    else:
                        # Direct string content
                        image_bytes = body.encode("utf-8")
                except json.JSONDecodeError:
                    # Direct string content (not JSON)
                    image_bytes = body.encode("utf-8")
            else:
                # Direct binary data
                image_bytes = body 

        # Detect file type from the first few bytes
        file_ext = "bin"  # default
        content_type = "application/octet-stream"  # default
        
        if image_bytes.startswith(b'\xff\xd8\xff'):
            file_ext = "jpg"
            content_type = "image/jpeg"
        elif image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            file_ext = "png"
            content_type = "image/png"
        elif image_bytes.startswith(b'GIF8'):
            file_ext = "gif"
            content_type = "image/gif"
        elif image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:12]:
            file_ext = "webp"
            content_type = "image/webp"
        
        filename = f"{uuid.uuid4()}.{file_ext}"

        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=image_bytes,
            ContentType=content_type
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Bucket '{bucket_name}' created, image uploaded as '{filename}'",
                'bucket': bucket_name,
                'key': filename
            })
        }

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
