# aws configure

import boto3

# Create IAM client
iam_client = boto3.client('iam')

# Create user
response = iam_client.create_user(
    UserName='IAM_USER_NAME'
)

print(response)

# via the Session

S3_session = boto3.Session(
    aws_access_key_id = ACCESS_KEY,
    aws_secret_access_key = SECRET_KEY,
    aws_session_token = SESSION_TOKEN,
)

S3_session = boto3.Session(profile_name='user1')

# Any clients created from this session will use credentials
# from the [user1] section of ~/.aws/credentials.

user1_s3_client = S3_session.client('s3')

