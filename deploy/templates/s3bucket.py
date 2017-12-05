from troposphere import Output, Ref, Template, Export, Sub
from troposphere.s3 import Bucket, Private


class openVpn(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.template.add_description(
            "This bucket will hold the certificates for openvpn to work")
        self.add_s3_bucket()
        self.add_s3_bucket_output()


    def add_s3_bucket(self):
        self.s3Bucket = self.template.add_resource(Bucket(
            self.sceptre_user_data["bucket_name"],
            AccessControl=Private,
            BucketName=self.sceptre_user_data["bucket_name"],
        ))

    def add_s3_bucket_output(self):
        self.s3BucketOutput = self.template.add_output(Output(
            "BucketName",
            Value=Ref(self.s3Bucket),
            Export=Export(Sub("${AWS::StackName}-s3bucketname")),
            Description="Name of S3 bucket to hold website content"
))

def sceptre_handler(sceptre_user_data):
    sceptre = openVpn(sceptre_user_data)
    return sceptre.template.to_json()
