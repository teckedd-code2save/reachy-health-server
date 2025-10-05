import boto3

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

try:
    s3.create_bucket(Bucket='file-management')
    print('Bucket created successfully')
except Exception as e:
    print(f'Error: {e}')
