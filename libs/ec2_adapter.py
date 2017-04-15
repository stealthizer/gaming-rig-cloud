from libs.boto_adapter import AWSBotoAdapter

class Ec2Adapter:

    def __init__(self, profile):
        self.__connection = AWSBotoAdapter()
        self.__resource = 'ec2'
        self.__profile = profile

    def __get_connection_ec2(self):
        return self.__connection.get_client(self.__resource, self.__profile)

    def get_password_data(self, instance):
        password = self.__get_connection_ec2().get_password_data(InstanceId=instance)
        return password['PasswordData']

    def get_ec2_instance_data(self, name):
        filters = [
            {
                'Name': 'tag:Name',
                'Values': [name]
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
        instance_data = []
        instances = self.__get_connection_ec2().describe_instances(Filters=filters)['Reservations']
        for instance in instances:
            instance_dict = {}
            if 'PublicDnsName' in instance['Instances'][0].keys():
                instance_dict['public_dns'] = instance['Instances'][0]['PublicDnsName']
            if 'InstanceId' in instance['Instances'][0].keys():
                instance_dict['InstanceId'] = instance['Instances'][0]['InstanceId']
            instance_data.append(instance_dict)
        return instance_data

