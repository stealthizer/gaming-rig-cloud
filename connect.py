from libs.ec2_adapter import Ec2Adapter
from libs.rsa_decrypt import decryptPasswordWindows
import argparse


parser = argparse.ArgumentParser(description='Creates a cloudfront distribution and related route53 needed')
parser.add_argument('-p', '--profile', required=True, help='profile of the AWS account')
args = parser.parse_args()
__profile = args.profile
__server_name = __profile

ec2client = Ec2Adapter(__profile)
instance_id = ec2client.get_ec2_instance_data(__server_name)[0]['InstanceId']
instance_dns = ec2client.get_ec2_instance_data(__server_name)[0]['public_dns']

password_data = ec2client.get_password_data(instance_id)
decrypt = decryptPasswordWindows(profile=__profile, password=password_data)
password = decrypt.decrypt_password()
print(password)
print(instance_id)
print(instance_dns)
