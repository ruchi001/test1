#
# Imports all necessary packages
#

import boto3
from boto3 import ec2
from botocore.exceptions import ClientError
from Logging import logger
import logging
from ConfigParser import SafeConfigParser


class Security:


    def readConfig(self):
        parser = SafeConfigParser()
        CONFIGURATION_FILE = "setting.conf"
        parser.read(CONFIGURATION_FILE)


        try:
            self.GroupIds = parser.get("Settings", "GroupIds")
            self.GroupName = parser.get("Settings", "GroupName")
            self.Description = parser.get("Settings", "Description")
            self.GroupId = parser.get("Settings", "GroupId")
            self.IpProtocol = parser.get("Settings", "IpProtocol")
            self.FromPort = int(parser.get("Settings", "FromPort"))
            self.ToPort = parser.get("Settings", "ToPort")
            self.IpRanges = parser.get("Setting", "IpRanges")
            self.UserName = int(parser.get("Settings", "UserName"))
            self.aws_access_key_id = parser.get("Settings", "aws_access_key_id")
            self.aws_secret_access_key = parser.get("Settings", "aws_secret_access_key")
            self.aws_session_token = parser.get("Settings", "aws_session_token")
            self.Profile_User_name = parser.get("Settings", "Profile_User_name)")
            self.SecurityGroupId = parser.get ("ingress", "SecurityGroupId")
            self.CidrIp= parser.get("ingress","CidrIp" )
            self.FromPort = parser.get("ingress", "FromPort")
            self.GroupName = parser.get("ingress","GroupName")
            self.FromPort = parser.get("ingress", "FromPort")
            self.IpProtocol = parser.get("ingress","IpProtocol")
            self.IpRanges_CidrIp = parser.get("ingress", "CidrIp")
            self.IpRanges_Description = parser.get("ingress","Description")
            self.Ipv6Ranges_CidrIpv6 = parser.get("ingress", "CidrIp")
            self.Ipv6Ranges_Description = parser.get("ingress","Description")
            self.PrefixListIds_PrefixListId = parser.get("ingress", "CidrIp")
            self.PrefixListIds_Description = parser.get("ingress","Description")
            self.ToPort = parser.get("ingress", "ToPort"),
            self.UserIdGroupPairs_Description = parser.get("ingress", "Description")
            self.UserIdGroupPairs_GroupName = parser.get("ingress", "GroupName")
            self.UserIdGroupPairs_GroupId = parser.get("ingress", "GroupId")
            self.UserIdGroupPairs_PeeringStatus = parser.get("ingress", "PeeringStatus")
            self.UserIdGroupPairs_UserId = parser.get("ingress", "UserId")
            self.UserIdGroupPairs_VpcId = parser.get("ingress", "VpcId")
            self.UserIdGroupPairs_VpcPeeringConnectionId = parser.get("ingress", "VpcPeeringConnectionId")
            self.IpProtocol = parser.get("ingress", "IpProtocol")
            self.SourceSecurityGroupName = parser.get("ingress", "SourceSecurityGroupName")
            self.SourceSecurityGroupOwnerId = parser.get("ingress", "SourceSecurityGroupOwnerId")
            self.ToPort = parser.get("ingress", "ToPort")
            self.DryRun = parser.get("ingress", "DryRun")

            self.DryRun = parser.get("egress", "DryRun")
            self.IpPermissions_FromPort = parser.get ("egress", "IpPermissions_FromPort")
            self.IpPermissions_IpProtocol = parser.get("egress", "IpPermissions_IpProtocol")
            self.CidrIp= parser.get("egress","CidrIp" )
            self.FromPort = parser.get("egress", "FromPort")
            self.GroupName = parser.get("egress","GroupName")
            self.FromPort = parser.get("egress", "FromPort")
            self.IpProtocol = parser.get("egress","IpProtocol")
            self.IpRanges_CidrIp = parser.get("egress", "CidrIp")
            self.IpRanges_Description = parser.get("egress","Description")
            self.Ipv6Ranges_CidrIpv6 = parser.get("egress", "CidrIp")
            self.Ipv6Ranges_Description = parser.get("egress","Description")
            self.PrefixListIds_PrefixListId = parser.get("egress", "CidrIp")
            self.PrefixListIds_Description = parser.get("egress","Description")
            self.ToPort = parser.get("egress", "ToPort"),
            self.UserIdGroupPairs_Description = parser.get("egress", "Description")
            self.UserIdGroupPairs_GroupName = parser.get("egress", "GroupName")
            self.UserIdGroupPairs_GroupId = parser.get("egress", "GroupId")
            self.UserIdGroupPairs_PeeringStatus = parser.get("egress", "PeeringStatus")
            self.UserIdGroupPairs_UserId = parser.get("egress", "UserId")
            self.UserIdGroupPairs_VpcId = parser.get("egress", "VpcId")
            self.UserIdGroupPairs_VpcPeeringConnectionId = parser.get("egress", "VpcPeeringConnectionId")
            self.CidrIp = parser.get("egress", "CidrIp")
            self.FromPort = parser.get("egress", "FromPort")
            self.ToPort = parser.get("egress", "ToPort")
            self.SourceSecurityGroupName = parser.get("egress", "SourceSecurityGroupName")
            self.SourceSecurityGroupOwnerId = parser.get("egress", "SourceSecurityGroupOwnerId")

        except Exception as error:
            logger.exception(error)


    # describe_security_groups

    ec2_client = boto3.client('ec2')

    def describe_security_groups(self):

        try:
            response_describe_security_groups = ec2.describe_security_groups(GroupIds=self.GroupIds)
            print(response_describe_security_groups)
        except ClientError as error:
            logger.exception(error)


    # create_security_group

    def create_security_group(self):

        ec2_client = boto3.client('ec2')

        response_describe_vpcs = ec2_client.describe_vpcs()

        vpc_id = response_describe_vpcs.get('Vpcs', [{}])[0].get('VpcId', '')

        try:
            response_create_security_group = ec2_client.create_security_group(GroupName=self.GroupName,
                                                                              Description=self.Description,
                                                                              VpcId=vpc_id
                                                    )

            security_group_id = response_create_security_group[self.GroupId]
            print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

            data = ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {'IpProtocol': self.IpProtocol,
                    'FromPort': self.FromPort,
                    'ToPort': self.ToPort,
                    'IpRanges': self.IpRanges},
                ]
            )
            print('Ingress Successfully Set %s' % data)

        except ClientError as error:
            logger.exception(error)


    # Create_IAM_client

    def create_IAM_client(self):

        iam_client = boto3.client('iam')

        # Create user

        try:
            response_create_user = iam_client.create_user(
                UserName=self.UserName
            )

            s3_session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                aws_session_token=self.aws_session_token,
            )

            s3_session = boto3.Session(profile_name= self.Profile_User_name)

            # Any clients created from this session will use credentials
            # from the [Profile_User_name] section of ~/.aws/credentials.

            user1_s3_client = s3_session.client('s3')
            print (user1_s3_client)

        except ClientError as error:
            logger.exception(error)


    # security_group_authorizetion_ingress(entery)

    def security_group_authorizetion_ingress(self):

        ec2_resource = boto3.resource('ec2')

        try:
            security_group = ec2_resource.SecurityGroup(self.SecurityGroupId)
            response_authorize_ingress = security_group.authorize_ingress(
                CidrIp=self.CidrIp,
                FromPort=int(self.FromPort),
                GroupName=self.GroupName,
                IpPermissions=[
                    {
                        'FromPort': int(self.FromPort),
                        'IpProtocol': self.IpProtocol,
                        'IpRanges': [
                            {
                                'CidrIp': self.IpRanges_CidrIp,
                                'Description': self.IpRanges_Description
                            },
                        ],
                        'Ipv6Ranges': [
                            {
                                'CidrIpv6': self.Ipv6Ranges_CidrIpv6,
                                'Description': self.Ipv6Ranges_Description
                            },
                        ],
                        'PrefixListIds': [
                            {
                                'Description': self.PrefixListIds_Description,
                                'PrefixListId': self.PrefixListIds_PrefixListId
                            },
                        ],
                        'ToPort': int(self.ToPort),
                        'UserIdGroupPairs': [
                            {
                                'Description': self.UserIdGroupPairs_Description,
                                'GroupId': self.UserIdGroupPairs_GroupId,
                                'GroupName': self.UserIdGroupPairs_GroupName,
                                'PeeringStatus': self.UserIdGroupPairs_PeeringStatus,
                                'UserId': self.UserIdGroupPairs_UserId,
                                'VpcId': self.UserIdGroupPairs_VpcId,
                                'VpcPeeringConnectionId': self.UserIdGroupPairs_VpcPeeringConnectionId
                            },
                        ]
                    },
                ],
                IpProtocol=self.IpProtocol,
                SourceSecurityGroupName=self.SourceSecurityGroupName,
                SourceSecurityGroupOwnerId=self.SourceSecurityGroupOwnerId,
                ToPort=self.ToPort,
                DryRun=self.DryRun
            )

        except ClientError as error:
            logger.exception(error)


    # security_group_authorizetion_egress(Exit)

    def security_group_authorizetion_egress(self):

        ec2_resource = boto3.resource('ec2')

        security_group = ec2_resource.SecurityGroup(self.SecurityGroupId)


        try:
            response_authorize_egress = security_group.authorize_egress(
                DryRun=True | False,
                IpPermissions=[
                    {
                        'FromPort': int(self.IpPermissions_FromPort),
                        'IpProtocol': self.IpPermissions_IpProtocol,
                        'IpRanges': [
                            {
                                'CidrIp': self.IpRanges_CidrIp,
                                'Description': self.IpRanges_Description
                            },
                        ],
                        'Ipv6Ranges': [
                            {
                                'CidrIpv6': self.Ipv6Ranges_CidrIpv6,
                                'Description': self.Ipv6Ranges_Description
                            },
                        ],
                        'PrefixListIds': [
                            {
                                'Description': self.PrefixListIds_Description ,
                                'PrefixListId': self.PrefixListIds_PrefixListId
                            },
                        ],
                        'ToPort': self.ToPort,
                        'UserIdGroupPairs': [
                            {
                                'Description': self.UserIdGroupPairs_Description,
                                'GroupId': self.UserIdGroupPairs_GroupId,
                                'GroupName': self.UserIdGroupPairs_GroupName,
                                'PeeringStatus': self.UserIdGroupPairs_PeeringStatus,
                                'UserId': self.UserIdGroupPairs_UserId,
                                'VpcId': self.UserIdGroupPairs_VpcId,
                                'VpcPeeringConnectionId': self.UserIdGroupPairs_VpcPeeringConnectionId
                            },
                        ]
                    },
                ],
                CidrIp= self.CidrIp,
                FromPort=self.FromPort,
                IpProtocol=self.IpProtocol,
                ToPort=self.ToPort,
                SourceSecurityGroupName=self.SourceSecurityGroupName,
                SourceSecurityGroupOwnerId=self.SourceSecurityGroupOwnerId
        )




        except ClientError as error:
            logger.exception(error)

    describe_security_groups()
    create_security_group()
    create_IAM_client()
    security_group_authorizetion_egress()
    security_group_authorizetion_ingress()
