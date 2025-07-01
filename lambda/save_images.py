import json
import boto3
import datetime
import base64
import uuid

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    try:
        bucket_name = f'upload-bucket-{datetime.datetime.now().strftime("%Y-%m-%d")}'

        existing_buckets = s3.list_buckets()
        if not any(b['Name'] == bucket_name for b in existing_buckets['Buckets']):
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': 'us-east-1'}
            )

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

        filename = f"{uuid.uuid4()}.jpg"

        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=image_bytes,
            ContentType='image/jpeg'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Bucket '{bucket_name}' created (if not exists), image uploaded as '{filename}'",
                'bucket': bucket_name,
                'key': filename
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
