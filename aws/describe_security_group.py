import boto

ec2 = boto.client('ec2')
ec2.describe_regions()

response = ec2.describe_availability_zones()
print ('Availability zones: ', response['AAvailabilityZones'])