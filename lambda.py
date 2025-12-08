#checking connection
import boto3

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    buckets = s3_client.list_buckets()
    
    
    return {
        'statusCode': 200,
        'body': buckets
    }
