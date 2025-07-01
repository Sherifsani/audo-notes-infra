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

        # Function to try base64 decoding
        def try_base64_decode(data_str):
            try:
                # Remove any whitespace and validate base64
                cleaned_data = data_str.strip()
                decoded = base64.b64decode(cleaned_data, validate=True)
                # Check if the decoded data looks like image binary data
                if (decoded.startswith(b'\xff\xd8\xff') or  # JPEG
                    decoded.startswith(b'\x89PNG\r\n\x1a\n') or  # PNG
                    decoded.startswith(b'GIF8') or  # GIF
                    decoded.startswith(b'RIFF')):  # WEBP
                    return decoded
                return None
            except Exception:
                return None

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
                            # Try base64 decoding even if not marked as base64
                            decoded = try_base64_decode(actual_body)
                            if decoded:
                                image_bytes = decoded
                            else:
                                image_bytes = actual_body.encode("utf-8")
                    else:
                        # Try base64 decoding first, fallback to string encoding
                        decoded = try_base64_decode(body)
                        if decoded:
                            image_bytes = decoded
                        else:
                            image_bytes = body.encode("utf-8")
                except json.JSONDecodeError:
                    # Try base64 decoding first, fallback to string encoding
                    decoded = try_base64_decode(body)
                    if decoded:
                        image_bytes = decoded
                    else:
                        image_bytes = body.encode("utf-8")
            else:
                # Direct binary data
                image_bytes = body 

        # Detect file type from the first few bytes
        file_ext = "bin"  # default
        content_type = "application/octet-stream"  # default
        
        # More comprehensive file type detection
        if len(image_bytes) >= 10:  # Ensure we have enough bytes to check
            if image_bytes.startswith(b'\xff\xd8\xff'):
                file_ext = "jpg"
                content_type = "image/jpeg"
            elif image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
                file_ext = "png"
                content_type = "image/png"
            elif image_bytes.startswith(b'GIF87a') or image_bytes.startswith(b'GIF89a'):
                file_ext = "gif"
                content_type = "image/gif"
            elif image_bytes.startswith(b'RIFF') and len(image_bytes) >= 12 and b'WEBP' in image_bytes[:12]:
                file_ext = "webp"
                content_type = "image/webp"
            elif image_bytes.startswith(b'BM'):  # Bitmap
                file_ext = "bmp"
                content_type = "image/bmp"
        
        logger.info(f"Detected file type: {file_ext}, content type: {content_type}, data size: {len(image_bytes)} bytes")
        
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
