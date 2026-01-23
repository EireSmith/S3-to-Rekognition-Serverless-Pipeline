# AWS Lambda Rekognition Integration

This Lambda function processes images uploaded to S3 and analyzes them using AWS Rekognition.

## Features

- **Label Detection**: Identifies objects, scenes, and concepts in images
- **Text Detection**: Extracts text from images (OCR)
- **Face Detection**: Detects faces and analyzes facial attributes (emotions, age range, etc.)
- **Error Handling**: Comprehensive error handling for AWS API failures
- **Format Validation**: Validates image formats (JPEG, JPG, PNG)

## Setup Instructions

### 1. Create IAM Role for Lambda

Create a role with the following permissions (see `lambda_iam_policy.json`):
- `s3:GetObject` - Read images from S3
- `rekognition:DetectLabels` - Detect objects and scenes
- `rekognition:DetectText` - Detect text in images
- `rekognition:DetectFaces` - Detect faces and attributes
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` - CloudWatch Logs

### 2. Create Lambda Function

1. Go to AWS Lambda Console
2. Create a new function
3. Choose "Author from scratch"
4. Function name: `image-rekognition-analyzer`
5. Runtime: Python 3.11 or later
6. Execution role: Select the IAM role created in step 1
7. Copy the code from `lambda_function.py` to the function code editor

### 3. Add S3 Trigger

1. In Lambda function configuration, add S3 trigger
2. S3 bucket: Select your image bucket
3. Event types: `s3:ObjectCreated:*`
4. Prefix: (optional) `images/` or similar
5. Suffix: `.jpg`, `.jpeg`, `.png`

### 4. Set Environment Variables (Optional)

Add these environment variables in Lambda configuration:
- `LOG_LEVEL`: `INFO` or `DEBUG`

### 5. Deploy

- Package: `lambda_function.py` (includes boto3 and rekognition which are pre-installed in Lambda)
- Create deployment package: `zip lambda_function.zip lambda_function.py`
- Upload to Lambda or use AWS CLI:
```bash
aws lambda update-function-code \
  --function-name image-rekognition-analyzer \
  --zip-file fileb://lambda_function.zip
```

## Testing

### Test with S3 Event

Use the sample S3 event in `test_event.json` to test the Lambda function:

1. Go to Lambda function
2. Click "Test"
3. Paste the event JSON
4. Click "Test"

### Test Locally

```python
from lambda_function import analyze_image_from_s3

# Analyze an image in S3
result = analyze_image_from_s3('your-bucket-name', 'path/to/image.jpg')
print(result)
```

## API Response Format

### Success Response (200)

```json
{
  "statusCode": 200,
  "body": {
    "bucket": "your-bucket",
    "key": "images/photo.jpg",
    "labels": [
      {
        "name": "Person",
        "confidence": 95.5,
        "instances": 2
      },
      {
        "name": "Face",
        "confidence": 92.3,
        "instances": 2
      }
    ],
    "text": [
      {
        "text": "Hello World",
        "confidence": 88.5,
        "geometry": {...}
      }
    ],
    "faces": [
      {
        "confidence": 99.8,
        "age_range": {"Low": 25, "High": 35},
        "smile": true,
        "gender": "Female",
        "emotions": [
          {"type": "HAPPY", "confidence": 95.2}
        ]
      }
    ]
  }
}
```

### Error Response (400/500)

```json
{
  "statusCode": 400,
  "body": {
    "error": "Invalid image format. Supported formats: JPEG, JPG, PNG"
  }
}
```

## Monitoring

View Lambda logs in CloudWatch:
1. Go to CloudWatch Console
2. Logs → Log Groups
3. Search for `/aws/lambda/image-rekognition-analyzer`

## Cost Optimization

- Adjust `MinConfidence` parameter (currently 70%) to reduce costs
- Adjust `MaxLabels` parameter (currently 10) to limit results
- Consider using S3 event filtering to skip non-image files

## Troubleshooting

### "Access Denied" Error
- Check IAM role has correct permissions
- Verify S3 bucket policy allows Lambda execution role

### "Invalid S3 object" Error
- Verify image file exists in S3
- Check image format is JPEG or PNG
- Ensure bucket name and key are correct

### Timeout
- Increase Lambda timeout (currently may need adjustment)
- Reduce image resolution if possible
- Check network connectivity to S3 and Rekognition APIs

## Customization

### Add Custom Labels Training
Use Amazon Rekognition Custom Labels for domain-specific image recognition.

### Save Results to DynamoDB
Add DynamoDB write permissions and store analysis results for querying.

### Send Notifications
Add SNS permissions to send notifications when specific labels are detected.

### Additional Rekognition Features
The library also supports:
- Content Moderation
- Celebrity Recognition
- Path Tracking
- Segment Detection
- Custom Labels
