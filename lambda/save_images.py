import json
import boto3
import base64
import os
import uuid
import mimetypes

# Initialize the S3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # --- 1. Get Bucket Name from Environment Variable ---
        bucket_name = os.environ.get('IMAGES_BUCKET')
        if not bucket_name:
            raise ValueError("BUCKET_NAME environment variable is not set.")

        # --- 2. Parse Request Body ---
        # For a standard JSON API, the body will be a JSON string.
        # We load it directly.
        body = event.get('body', '{}')
        payload = json.loads(body)

        # --- 3. Extract Image Data and File Name ---
        image_base64 = payload.get('image')
        file_name = payload.get('fileName')

        if not image_base64 or not file_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing "image" or "fileName" in request body.'})
            }

        # Decode the base64 string to get the binary image data
        image_data = base64.b64decode(image_base64)

        # --- 4. Generate a Unique Key for S3 ---
        unique_id = uuid.uuid4()
        s3_key = f"uploads/{unique_id}-{file_name}"

        # --- 5. Determine Content Type ---
        # Guess the MIME type of the file based on its extension
        content_type = mimetypes.guess_type(file_name)[0]
        if not content_type:
            content_type = 'application/octet-stream' # Default if type cannot be determined

        # --- 6. Upload to S3 ---
        # The PutObject operation uploads the data to the specified bucket.
        # We now include the ContentType.
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=image_data,
            ContentType=content_type
        )

        # --- 7. Generate a Presigned URL (Optional but useful) ---
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=3600
        )

        # --- 8. Return Success Response ---
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*' # Add CORS headers if needed
            },
            'body': json.dumps({
                'message': 'Image uploaded successfully!',
                's3_key': s3_key,
                'presigned_url': presigned_url,
                'contentType': content_type
            })
        }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid JSON in request body.'})
        }
    except (TypeError, base64.binascii.Error) as e:
         return {
            'statusCode': 400,
            'body': json.dumps({'message': f'Invalid base64 encoding for image: {str(e)}'})
        }
    except Exception as e:
        # Generic error handler for unexpected issues
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }
