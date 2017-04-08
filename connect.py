from libs.ec2_adapter import Ec2Adapter
from libs.rsa_decrypt import decryptPasswordWindows

profile = 'your-profile'
server_name = 'your-server-name'

ec2client = Ec2Adapter(profile)
instance_id = ec2client.get_ec2_instance_data(server_name)[0]['InstanceId']
instance_dns = ec2client.get_ec2_instance_data(server_name)[0]['public_dns']

password_data = ec2client.get_password_data(instance_id)
decrypt = decryptPasswordWindows(profile=profile, password=password_data)
password = decrypt.decrypt_password()
print(password)
print(instance_id)
print(instance_dns)
