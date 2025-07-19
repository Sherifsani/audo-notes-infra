import os
import boto3
import json
import urllib.parse as urlparse
import datetime

textract = boto3.client("textract")
s3 = boto3.client("s3")
polly = boto3.client("polly")

def lambda_handler(event, context):
    try:
        audio_bucket = os.environ.get('AUDIO_BUCKET')
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = urlparse.unquote_plus(record['s3']['object']['key'])

        response = textract.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            }
        )

        extracted_text = ""
        for block in response["Blocks"]:
            if block["BlockType"] == "LINE":
                extracted_text += block["Text"] + "\n"
        print(f"Extracted text from {key}:\n{extracted_text}")
        
        # Convert text to audio using Polly
        if extracted_text.strip():  # Only proceed if there's text to convert
            try:
                # Use Polly to synthesize speech
                polly_response = polly.synthesize_speech(
                    Text=extracted_text,
                    OutputFormat='mp3',
                    VoiceId='Joanna',  # You can change this to other voices like 'Matthew', 'Amy', etc.
                    Engine='neural'    # Use neural engine for better quality (optional)
                )
                
                # Generate audio file name based on original image file
                audio_key = key.rsplit('.', 1)[0] + '_audio.mp3'
                
                # Save audio to S3
                s3.put_object(
                    Bucket=audio_bucket,  # Replace with your audio bucket name
                    Key=audio_key,
                    Body=polly_response['AudioStream'].read(),
                    ContentType='audio/mpeg',
                    Metadata={
                        'source-image': key,
                        'text-length': str(len(extracted_text)),
                        'voice-id': 'joanna',
                        'processing-date': datetime.datetime.now().isoformat()
                    }
                )
                
                print(f"Audio file saved to {bucket}/{audio_key}")
                
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "message": f"Text extracted and converted to audio",
                        "text_file": key,
                        "audio_file": audio_key,
                        "extracted_text": extracted_text
                    })
                }
            except Exception as polly_error:
                print(f"Error with Polly conversion: {str(polly_error)}")
                # Return the extracted text even if Polly fails
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "message": f"Text extracted but audio conversion failed",
                        "text_file": key,
                        "extracted_text": extracted_text,
                        "polly_error": str(polly_error)
                    })
                }
        else:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "No text found in the image",
                    "text_file": key
                })
            }

    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "bucket": bucket if 'bucket' in locals() else "unknown",
                "key": key if 'key' in locals() else "unknown"
            })
        }