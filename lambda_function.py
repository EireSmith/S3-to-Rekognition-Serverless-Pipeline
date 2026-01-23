import boto3
import json
import os
from botocore.exceptions import ClientError

# Initialize AWS clients
s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')


def lambda_handler(event, context):
    """
    Lambda function to process S3 image uploads and send them to AWS Rekognition.
    
    Expected S3 event structure:
    {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "bucket-name"
                    },
                    "object": {
                        "key": "image-key"
                    }
                }
            }
        ]
    }
    """
    
    try:
        # Extract bucket and key from S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        print(f"Processing image: s3://{bucket}/{key}")
        
        # Verify the file is an image
        if not is_valid_image_format(key):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid image format. Supported formats: JPEG, JPG, PNG'
                })
            }
        
        # Send image to Rekognition for label detection
        labels_result = detect_labels(bucket, key)
        
        # Send image to Rekognition for text detection (optional)
        text_result = detect_text(bucket, key)
        
        # Send image to Rekognition for face detection (optional)
        faces_result = detect_faces(bucket, key)
        
        # Combine results
        response_data = {
            'bucket': bucket,
            'key': key,
            'labels': labels_result,
            'text': text_result,
            'faces': faces_result
        }
        
        print(f"Successfully processed image: {key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(response_data)
        }
        
    except KeyError as e:
        print(f"KeyError: Missing expected field in event: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid S3 event structure: {str(e)}'})
        }
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"AWS Client Error ({error_code}): {error_message}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'AWS Error: {error_message}'})
        }
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Unexpected error: {str(e)}'})
        }


def is_valid_image_format(key):
    """Check if the file has a valid image extension."""
    valid_extensions = ('.jpg', '.jpeg', '.png')
    return key.lower().endswith(valid_extensions)


def detect_labels(bucket, key):
    """
    Detect objects and scenes in the image using Rekognition Labels.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
    
    Returns:
        List of detected labels with confidence scores
    """
    try:
        response = rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            },
            MaxLabels=10,
            MinConfidence=70
        )
        
        labels = []
        for label in response['Labels']:
            labels.append({
                'name': label['Name'],
                'confidence': label['Confidence'],
                'instances': len(label.get('Instances', []))
            })
        
        print(f"Detected {len(labels)} labels in image")
        return labels
        
    except ClientError as e:
        print(f"Error detecting labels: {e}")
        raise


def detect_text(bucket, key):
    """
    Detect text in the image using Rekognition Text Detection.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
    
    Returns:
        List of detected text blocks
    """
    try:
        response = rekognition_client.detect_text(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            }
        )
        
        text_detections = []
        for detection in response['TextDetections']:
            if detection['Type'] == 'LINE':  # Get lines instead of individual words
                text_detections.append({
                    'text': detection['DetectedText'],
                    'confidence': detection['Confidence'],
                    'geometry': detection['Geometry']['BoundingBox']
                })
        
        print(f"Detected {len(text_detections)} text lines in image")
        return text_detections
        
    except ClientError as e:
        print(f"Error detecting text: {e}")
        return []


def detect_faces(bucket, key):
    """
    Detect faces in the image using Rekognition Face Detection.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
    
    Returns:
        List of detected faces with attributes
    """
    try:
        response = rekognition_client.detect_faces(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            },
            Attributes=['ALL']
        )
        
        faces = []
        for face in response['FaceDetails']:
            faces.append({
                'confidence': face['Confidence'],
                'age_range': face['AgeRange'],
                'smile': face['Smile']['Value'],
                'gender': face['Gender']['Value'],
                'eyes_open': face['EyesOpen']['Value'],
                'mouth_open': face['MouthOpen']['Value'],
                'emotions': [
                    {
                        'type': emotion['Type'],
                        'confidence': emotion['Confidence']
                    }
                    for emotion in face['Emotions']
                ]
            })
        
        print(f"Detected {len(faces)} faces in image")
        return faces
        
    except ClientError as e:
        print(f"Error detecting faces: {e}")
        return []


# Alternative function to call Rekognition directly with local file path
def analyze_image_from_s3(bucket, key):
    """
    Simplified function to analyze an image from S3.
    Can be called directly without S3 trigger event.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
    
    Returns:
        Dictionary with analysis results
    """
    try:
        return {
            'labels': detect_labels(bucket, key),
            'text': detect_text(bucket, key),
            'faces': detect_faces(bucket, key)
        }
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        raise
