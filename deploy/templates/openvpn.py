from troposphere import Base64, FindInMap, GetAtt
from troposphere import Parameter, Output, Ref, Template, Tags, ImportValue, cloudformation, Join
import troposphere.ec2 as ec2
import troposphere.iam as iam

class openVpn(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.ami_mapping()
        self.add_security_group()
        self.add_iam_role()
        self.add_ec2_instance()
        self.add_output()

    def ami_mapping(self):
        self.template.add_mapping('RegionMap', {
            "eu-west-1": {"AMI": "ami-7d50491b"}
        })

    def add_security_group(self):
        self.securityGroup = self.template.add_resource(ec2.SecurityGroup(
            'VpnSecurityGroup',
            GroupDescription = "Allow access to openVpn",
            VpcId = ImportValue('deploy-dev-vpc-VPCId'),
            SecurityGroupIngress = [
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="22",
                    ToPort="22",
                    CidrIp="0.0.0.0/0"
                )],
            Tags=Tags(
                Name='vpnserver-sg'),
        ))

    def add_iam_role(self):
        self.iam_role=self.template.add_resource(iam.Role(
            "DescribeEc2AndStackRole",
            Path="/",
            AssumeRolePolicyDocument={"Statement": [{
                "Effect": "Allow",
                "Principal": {
                    "Service": [ "ec2.amazonaws.com" ]
                },
                "Action": [ "sts:AssumeRole" ]
            }]},
            Policies=[
                iam.Policy(
                    PolicyName="ListAllMyBuckets",
                    PolicyDocument={
                        "Statement": [{
                            "Effect": "Allow",
                            "Action": "s3:ListAllMyBuckets",
                            "Resource": "arn:aws:s3:::*"
                        }],
                    }
                ),
                iam.Policy(
                    PolicyName="AllowAccessToBucket",
                    PolicyDocument={
                        "Statement": [{
                            "Effect": "Allow",
                            "Action": [
                                "s3:ListBucket",
                                "s3:GetBucketLocation"
                            ],
                            "Resource": Join("", [ "arn:aws:s3:::", ImportValue('deploy-dev-s3bucket-s3bucketname')])
                        }]
                    }
                ),
                iam.Policy(
                    PolicyName="AllowWriteToBucket",
                    PolicyDocument={
                        "Statement": [{
                            "Effect": "Allow",
                            "Action": [
                                "s3:PutObject",
                                "s3:GetObject",
                                "s3:DeleteObject"
                                ],
                            "Resource": Join("", [ "arn:aws:s3:::", ImportValue('deploy-dev-s3bucket-s3bucketname'), "/*" ])
                        }]
                    }
                )
            ],
        ))
        self.cfninstanceprofile = self.template.add_resource(iam.InstanceProfile(
            "CFNInstanceProfile",
            Roles=[Ref(self.iam_role)]))


    def add_ec2_instance(self):
        self.ec2_instance = self.template.add_resource(ec2.Instance(
            "OpenVpn",
            ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
            InstanceType="t2.micro",
            KeyName=self.sceptre_user_data["keyname"],
            SecurityGroupIds=[Ref(self.securityGroup)],
            IamInstanceProfile=Ref(self.cfninstanceprofile),
            SubnetId=ImportValue('deploy-dev-vpc-PublicSubnet'),
            Metadata=cloudformation.Metadata(
                cloudformation.Init(
                    cloudformation.InitConfigSets(
                        ascending=['config1'],
                        descending=['config1']
                    ),
                    config1=cloudformation.InitConfig(
                        commands={
                            'test': {
                                'command': 'echo "$CFNTEST" > text.txt',
                                'env': {
                                    'CFNTEST': 'I come from config1.'
                                },
                                'cwd': '~'
                            }
                        }
                    )
                )
            ),
            UserData=Base64("80"),
            Tags=Tags(
                Name="vpn-server")
        ))

    def add_output(self):
        self.template.add_output([
            Output(
                "InstanceId",
                Description="InstanceId of the newly created EC2 instance",
                Value=Ref(self.ec2_instance),
            ),
            Output(
                "AZ",
                Description="Availability Zone of the newly created EC2 instance",
                Value=GetAtt(self.ec2_instance, "AvailabilityZone"),
            ),
            Output(
                "PublicIP",
                Description="Public IP address of the newly created EC2 instance",
                Value=GetAtt(self.ec2_instance, "PublicIp"),
            ),
            Output(
                "PrivateIP",
                Description="Private IP address of the newly created EC2 instance",
                Value=GetAtt(self.ec2_instance, "PrivateIp"),
            ),
            Output(
                "PublicDNS",
                Description="Public DNSName of the newly created EC2 instance",
                Value=GetAtt(self.ec2_instance, "PublicDnsName"),
            ),
            Output(
                "PrivateDNS",
                Description="Private DNSName of the newly created EC2 instance",
                Value=GetAtt(self.ec2_instance, "PrivateDnsName"),
            ),
        ])

def sceptre_handler(sceptre_user_data):
    sceptre = openVpn(sceptre_user_data)
    return sceptre.template.to_json()
