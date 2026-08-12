# AWS Rekognition Image Analysis Pipeline WIP

Uploads an image to S3 and automatically analyzes it with AWS Rekognition

## How it works

1. **`main.py`** validates a local image (JPEG/JPG/PNG) with Pillow and uploads it to an S3 bucket.
2. **S3** fires an `ObjectCreated` event when the upload lands.
3. **`lambda_function.py`** is triggered by that event, and runs the image through three Rekognition checks in parallel:
   - **Label detection** — objects, scenes, and concepts in the image
   - **Text detection** — OCR, line by line
   - **Face detection** — age range, emotions, smile, eyes/mouth open, per face found
4. Results are returned as a single combined JSON response and logged to CloudWatch.

```
Local image → main.py → S3 upload → S3 event → Lambda → Rekognition (labels / text / faces) → JSON result
```

## Repo structure

| File | Purpose |
|---|---|
| `main.py` | Local script: validates an image and uploads it to S3 |
| `add_user_data.py` | Validates image format ahead of upload |
| `lambda_function.py` | The Lambda handler — runs Rekognition label/text/face detection and returns the combined result |
| `lambda_iam_policy.json` | IAM permissions required by the Lambda execution role |
| `test_event.json` | Sample S3 event, for testing the Lambda function directly in the console |
| `LAMBDA_SETUP.md` | Full step-by-step AWS deployment guide — IAM role, function creation, S3 trigger, testing, troubleshooting |
| `test_data/` | Sample images used for local testing |
| `requirements.txt` | Python dependencies |

For full deployment instructions (IAM role setup, creating the Lambda function, wiring up the S3 trigger), see **[LAMBDA_SETUP.md](./LAMBDA_SETUP.md)**.

## Running the uploader locally

```bash
pip install -r requirements.txt
export AWS_S3_BUCKET=your-bucket-name
python main.py
```

Requires AWS credentials configured locally (`aws configure` or environment variables) with permission to upload to the target bucket.

## Example response

```json
{
  "statusCode": 200,
  "body": {
    "bucket": "your-bucket",
    "key": "images/photo.jpg",
    "labels": [
      { "name": "Person", "confidence": 95.5, "instances": 2 }
    ],
    "text": [
      { "text": "Hello World", "confidence": 88.5, "geometry": {} }
    ],
    "faces": [
      {
        "confidence": 99.8,
        "age_range": { "Low": 25, "High": 35 },
        "smile": true,
        "gender": "Female",
        "emotions": [{ "type": "HAPPY", "confidence": 95.2 }]
      }
    ]
  }
}
```

## Tech stack

Python · boto3 · AWS S3 · AWS Lambda · AWS Rekognition · Pillow

## Known limitations

- **`add_user_data()` doesn't yet do what its name says.** It currently just re-validates the image format — the actual "attach user metadata" logic (writing to `metadata_file`) hasn't been implemented yet.
- **No `.env.example`** documenting required environment variables (`AWS_S3_BUCKET`, AWS credentials).
- **No automated tests** beyond manually running the provided `test_event.json` against the deployed Lambda function.
##No Ai was used except README
