# coding: utf-8
from troposphere import Base64, FindInMap, GetAtt, GetAZs
from troposphere import Parameter, Output, Ref, Template, Tags, ImportValue, cloudformation, Join
import troposphere.ec2 as ec2
import troposphere.iam as iam
from troposphere.cloudformation import Init, InitFile, InitFiles, InitConfig, InitService, InitServices
from troposphere.policies import CreationPolicy, ResourceSignal
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration, Metadata, Tag

class gameMachine(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.ami_mapping()
        self.add_security_group()
        self.add_iam_role()
        self.add_launch_config()
        self.add_autoscaling_group()


    def ami_mapping(self):
        self.template.add_mapping('RegionMap', {
            "eu-west-1": {"AMI": "ami-dd0e0abb"}
        })

    def add_security_group(self):
        self.securityGroup = self.template.add_resource(ec2.SecurityGroup(
            'GameMachineSecurityGroup',
            GroupDescription = "Allow access to openVpn",
            VpcId = ImportValue('deploy-dev-vpc-VPCId'),
            SecurityGroupIngress = [
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="3389",
                    ToPort="3389",
                    CidrIp="172.16.0.0/24"
                )
            ],
            Tags=Tags(
                Name='SgGameMachine')
        )
        )

    def add_iam_role(self):
        self.iam_role = self.template.add_resource(iam.Role(
            "s3AcessPolicies",
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
            ]
        )
        )
        self.cfninstanceprofile = self.template.add_resource(iam.InstanceProfile(
            "CFNInstanceProfile",
            Roles=[
                Ref(self.iam_role)
            ]
        ))

    def add_ec2_instance(self):
        self.ec2_instance = self.template.add_resource(ec2.Instance(
            "GameMachine",
            ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
            InstanceType="t2.micro",
            KeyName=self.sceptre_user_data["keyname"],
            SecurityGroupIds=[Ref(self.securityGroup)],
            IamInstanceProfile=Ref(self.cfninstanceprofile),
            SubnetId=ImportValue('deploy-dev-vpc-PrivateSubnet'),
            UserData=Base64(
                Join(
                    '',
                    [
                        '','\n',
                    ])),
            CreationPolicy=CreationPolicy(
                ResourceSignal=ResourceSignal([[]]
                    Timeout='PT30M')),
            Tags=Tags(
                Name="game-machine"),
        )
        )

    def add_launch_config(self):
        self.launch_config = self.template.add_resource(LaunchConfiguration(
            "GameMachineLaunchConfig",
            KeyName=self.sceptre_user_data["keyname"],
            InstanceType="t2.micro",
            ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
            SecurityGroups=[Ref(self.securityGroup)],
            UserData=Base64(
                Join(
                    '',
                    [
                        '','\n',
                    ])),
            CreationPolicy=CreationPolicy(
                ResourceSignal=ResourceSignal(
                    Timeout='PT30M'))
        ))

    def add_autoscaling_group(self):
        self.autoscaling_group = self.template.add_resource(AutoScalingGroup(
            "GameMachineAutoscalingGroup",
            LaunchConfigurationName=Ref(self.launch_config),
            MinSize="1",
            MaxSize="1",
            DesiredCapacity="1",
            VPCZoneIdentifier=[ImportValue('deploy-dev-vpc-PrivateSubnet')],
            Tags=[
                Tag("Name", "GameMachine", True)
            ],
        ))


    def add_output(self):
        self.template.add_output([
            Output(
                "AZ",
                Description="Availability Zone of the newly created EC2 instance",
                Value=GetAtt(self.ec2_instance, "AvailabilityZone"),
            )
        ])

def sceptre_handler(sceptre_user_data):
    sceptre = gameMachine(sceptre_user_data)
    return sceptre.template.to_json()
