import json
import os
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Handle CORS preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': ''
        }
    
    try:
        bucket_name = os.environ.get('AUDIO_BUCKET')
        if not bucket_name:
            raise ValueError("AUDIO_BUCKET environment variable is not set.")
        
        response = s3.list_objects_v2(Bucket=bucket_name)

        if 'Contents' in response:
            # Get the most recent audio file
            latest_file = max(response['Contents'], key=lambda x: x['LastModified'])
            
            presigned_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': latest_file['Key']},
                ExpiresIn=3600  # URL valid for 1 hour
            )
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({
                    'audioUrl': presigned_url,
                    'fileName': latest_file['Key']
                })
            }
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'No audio files found',
                    'message': 'Please wait for processing to complete'
                })
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Failed to retrieve audio files',
                'message': str(e)
            })
        }