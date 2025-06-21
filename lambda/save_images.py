import json
import boto3
import datetime

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    try:
        bucket_name = f'upload-bucket-{datetime.datetime.now().strftime("%Y-%m-%d")}'
        s3.create_bucket(
            Bucket = bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': 'us-east-1'
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Bucket {bucket_name} created successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }