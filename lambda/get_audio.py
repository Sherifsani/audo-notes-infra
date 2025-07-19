import json
import os
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        bucket_name = os.environ.get('AUDIO_BUCKET')
        if not bucket_name:
            raise ValueError("AUDIO_BUCKET environment variable is not set.")
        
        response = s3.list_objects_v2(Bucket=bucket_name)

        audio_files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                meta_data = s3.head_object(
                    Bucket = bucket_name,
                    Key = obj['Key']
                )
            presigned_url = s3.generate_presigned_url(
                'get_object',
                params={'Bucket': bucket_name, 'Key': obj['Key']},
                ExpiresIn=3600  # URL valid for 1 hour
            )
            audio_files.append({
                'key': obj['key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat(),
                'download_url': presigned_url,
                'metadata': meta_data.get('Metadata',{})
            })
        return{
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Found {len(audio_files)} audio files',
                'audio_files': audio_files
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error retrieving environment variable: {str(e)}'})
        }