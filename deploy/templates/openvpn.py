# coding: utf-8
from troposphere import Base64, FindInMap, GetAtt
from troposphere import Parameter, Output, Ref, Template, Tags, ImportValue, cloudformation, Join
import troposphere.ec2 as ec2
import troposphere.iam as iam
from troposphere.cloudformation import Init, InitFile, InitFiles, InitConfig, InitService, InitServices
from troposphere.autoscaling import Metadata
from troposphere.policies import CreationPolicy, ResourceSignal
from troposphere.ec2 import NetworkInterfaceProperty, NetworkInterface

class openVpn(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.ami_mapping()
        self.add_security_group()
        self.add_iam_role()
        self.add_private_network_interface()
        self.add_ec2_instance()
        self.add_private_network_interface_attachment()
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
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="1194",
                    ToPort="1194",
                    CidrIp="0.0.0.0/0"
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="udp",
                    FromPort="1194",
                    ToPort="1194",
                    CidrIp="0.0.0.0/0"
                )
            ],
            Tags=Tags(
                Name='SgOpenVpn')
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

    def add_private_network_interface(self):
        self.private_interface = self.template.add_resource(NetworkInterface(
            "Eth1",
            Description="eth1",
            GroupSet=[ Ref(self.securityGroup)],
            SourceDestCheck=True,
            SubnetId=ImportValue('deploy-dev-vpc-PrivateSubnet'),
            Tags=Tags(
                Name="private_vpn_interface",
                Interface="eth1",
            ),

        ))



    def add_ec2_instance(self):

        instance_metadata = Metadata(
            Init({
                'config': InitConfig(
                    packages={
                        'yum': {
                            'openvpn': []
                        }
                    },
                    files=InitFiles({
                        '/etc/openvpn/server.conf': InitFile(
                            content=Join('\n', [
                                'port 1194',
                                'proto tcp-server',
                                'dev tun1',
                                'ifconfig 172.16.1.2 172.16.1.3',
                                'status server-tcp.log',
                                'verb 3',
                                'secret /etc/openvpn/static.key',
                                'keepalive 10 60',
                                'ping-timer-rem',
                                'persist-tun',
                                'persist-key',
                                'user nobody',
                                'group nobody',
                                'daemon',
                            ]
                         ),
                         mode='000644',
                         owner='root',
                         group='root'),

                        '/etc/openvpn/client.ovpn': InitFile(
                            content=Join('\n', [
                                'proto tcp-client',
                                'remote {{public_ip}}',
                                'port 1194',
                                'dev tun',
                                'secret /tmp/secret.key',
                                'ifconfig 10.4.0.2 10.4.0.1',
                            ]
                        ),
                        mode='000644',
                        owner='root',
                        group='root'),

                        '/etc/cfn/cfn-hup.conf': InitFile(
                            content=Join('',
                                [
                                '[main]\n',
                                'stack=', Ref('AWS::StackId'), '\n',
                                'region=', Ref('AWS::Region'),'\n',
                                 ]),
                              mode='000400',
                              owner='root',
                              group='root'),
                        '/etc/cfn/hooks.d/cfn-auto-reloader.conf': InitFile(
                            content=Join('', [
                                '[cfn-auto-reloader-hook]\n',
                                'triggers=post.update\n',
                                'path=Resources.OpenVpn.Metadata.AWS::CloudFormation::Init\n',
                                'action=/opt/aws/bin/cfn-init -v --stack ', Ref('AWS::StackName'),
                                '--resource OpenVpn ', ' --region ', Ref('AWS::Region'), '\n','runas=root\n',
                                ]
                            )
                        )
                    }
                    ),
                    services={
                        'sysvinit': InitServices({
                            'openvpn': InitService(
                                enabled=True,
                                ensureRunning=True,
                                files=[
                                    '/etc/openvpn/server.conf'
                                ]),
                            'cfn-hup': InitService(
                                enabled=True,
                                ensureRunning=True,
                                files=[
                                    '/etc/cfn/cfn-hup.conf',
                                    '/etc/cfn/hooks.d/cfn-auto-reloader.conf'
                                ])
                        }
                        )
                    }
                )
            }
            )
        )

        self.ec2_instance = self.template.add_resource(ec2.Instance(
            "OpenVpn",
            ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
            InstanceType="t2.micro",
            KeyName=self.sceptre_user_data["keyname"],
            SecurityGroupIds=[Ref(self.securityGroup)],
            IamInstanceProfile=Ref(self.cfninstanceprofile),
            SubnetId=ImportValue('deploy-dev-vpc-PublicSubnet'),
            Metadata=instance_metadata,
            UserData=Base64(
                Join(
                    '',
                    [
                        '#!/bin/bash -xe\n',
                        'yum install easy-rsa -y --enablerepo=epel\n',
                        'yum update -y aws-cfn-bootstrap\n',
                        '/opt/aws/bin/cfn-init -v --stack ', Ref('AWS::StackName'), ' --resource OpenVpn --region ',
                        Ref('AWS::Region'), '\n',
                        '/opt/aws/bin/cfn-signal -e $? --stack ', Ref('AWS::StackName'), ' --resource OpenVpn --region ',
                        Ref('AWS::Region'), '\n',
                        'cd /etc/openvpn\n',
                        'openvpn --genkey --secret static.key\n',
                        'aws s3 cp static.key s3://',ImportValue('deploy-dev-s3bucket-s3bucketname'),'/\n',
                        'sudo modprobe iptable_nat','\n',
                        'echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward','\n',
                        'sudo iptables -t nat -A POSTROUTING -s 10.4.0.1/2 -o eth0 -j MASQUERADE','\n',
                        'external_ip=`curl http://169.254.169.254/latest/meta-data/public-ipv4`','\n',
                        'sed -i "s|{{public_ip}}|$external_ip|g" /etc/openvpn/client.ovpn','\n',
                        'aws s3 cp client.ovpn s3://',ImportValue('deploy-dev-s3bucket-s3bucketname'),'\n',
                    ])),
            CreationPolicy=CreationPolicy(
                ResourceSignal=ResourceSignal(
                    Timeout='PT15M')),
            Tags=Tags(
                Name="vpn-server"),
        )
        )

    def add_private_network_interface_attachment(self):
        self.private_network_interface_attachment = self.template.add_resource(ec2.NetworkInterfaceAttachment(
            "attachment",
            DeleteOnTermination=True,
            InstanceId=Ref(self.ec2_instance),
            NetworkInterfaceId=Ref(self.private_interface),
            DeviceIndex="1",
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
            )
        ])

def sceptre_handler(sceptre_user_data):
    sceptre = openVpn(sceptre_user_data)
    return sceptre.template.to_json()
