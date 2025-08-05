import json
import boto3
import base64
from datetime import datetime
import uuid

def lambda_handler(event, context):
    try:
        s3_client = boto3.client('s3')
        bucket_name = 'your-bucket-name'

        # Handle different input formats
        image_data = None
        content_type = 'image/jpeg'

        # Method 1: Direct binary upload (multipart/form-data)
        if event.get('isBase64Encoded', False):
            image_data = base64.b64decode(event['body'])
            content_type = event.get('headers', {}).get('content-type', 'image/jpeg')

        # Method 2: JSON payload with base64 image
        elif event.get('body'):
            try:
                body = json.loads(event['body'])
                if 'image' in body:
                    # Remove data URL prefix if present (data:image/jpeg;base64,)
                    image_base64 = body['image']
                    if image_base64.startswith('data:'):
                        image_base64 = image_base64.split(',')[1]

                    image_data = base64.b64decode(image_base64)
                    content_type = body.get('contentType', 'image/jpeg')
            except json.JSONDecodeError:
                # Assume the body is raw base64
                image_data = base64.b64decode(event['body'])

        if not image_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No image data found'})
            }

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        extension = content_type.split('/')[-1] if '/' in content_type else 'jpg'
        filename = f"uploads/{timestamp}_{unique_id}.{extension}"

        # Upload to S3
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=image_data,
            ContentType=content_type,
            ServerSideEncryption='AES256'  # Optional: encrypt at rest
        )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'filename': filename,
                'size': len(image_data),
                'etag': response['ETag']
            })
        }

    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Upload failed',
                'message': str(e)
            })
        }
