import boto3

ec2 = boto3.client('ec2')

# Retrieves all regions/endpoints that work with EC2
response = ec2.describe_regions()
print('Regions:', response['Regions'])

# Retrieves availability zones only for region of the ec2 object
response = ec2.describe_availability_zones()

# access key for different user

[default]
aws_access_key_id = foo
aws_secret_access_key=bar

[profile dev]
aws_access_key_id=foo2
aws_secret_access_key=bar2

[profile prod]
aws_access_key_id=foo3
aws_secret_access_key=bar3