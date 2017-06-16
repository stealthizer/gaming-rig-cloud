from troposphere import Template, Parameter, Ref, GetAtt, Output
from troposphere.ec2 import VPC, Subnet, InternetGateway, VPCGatewayAttachment, RouteTable, SubnetRouteTableAssociation, Route, EIP, NatGateway


class Vpc(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.add_vpc()
        self.add_internet_gateway()
        self.add_public_net()
        self.add_private_net()
        self.add_net_gw_vpc_attachment()
        self.add_public_route_table()
        self.add_private_route_table()
        self.add_public_route_association()
        self.add_private_route_association()
        self.add_default_public_route()
        self.add_nat_eip()
        self.add_nat_gateway()
        self.add_nat_gateway_route()
        self.add_public_net_output()
        self.add_private_net_output()
        self.add_internet_gateway_output()
        self.add_vpc_output()
        self.add_nat_eip_output()

    def add_vpc(self):
        self.vpc = self.template.add_resource(VPC(
            "VPC",
            CidrBlock=self.sceptre_user_data["cidr_block"]
        ))

    def add_public_net(self):
        self.public_net = self.template.add_resource(Subnet(
            'PublicSubnet',
            CidrBlock=self.sceptre_user_data["public_subnet"],
            MapPublicIpOnLaunch=True,
            VpcId=Ref("VPC"),
        ))

    def add_private_net(self):
        self.private_net = self.template.add_resource(Subnet(
            'PrivateSubnet',
            CidrBlock=self.sceptre_user_data["private_subnet"],
            MapPublicIpOnLaunch=False,
            VpcId=Ref(self.vpc),
        ))

    def add_internet_gateway(self):
        self.internet_gateway = self.template.add_resource(InternetGateway(
            'InternetGateway',
        ))

    def add_net_gw_vpc_attachment(self):
        self.net_gw_vpc_attachment = self.template.add_resource(VPCGatewayAttachment(
            "NatAttachment",
            VpcId=Ref(self.vpc),
            InternetGatewayId=Ref(self.internet_gateway),
        ))

    def add_private_route_table(self):
        self.private_route_table = self.template.add_resource(RouteTable(
            'PrivateRouteTable',
            VpcId=Ref(self.vpc),
        ))

    def add_public_route_table(self):
        self.public_route_table = self.template.add_resource(RouteTable(
            'PublicRouteTable',
            VpcId=Ref(self.vpc),
        ))
    def add_public_route_association(self):
        self.public_route_association = self.template.add_resource(SubnetRouteTableAssociation(
            'PublicRouteAssociation',
            SubnetId=Ref(self.public_net),
            RouteTableId=Ref(self.public_route_table),
        ))
    def add_default_public_route(self):
        self.default_public_route = self.template.add_resource(Route(
            'PublicDefaultRoute',
            RouteTableId=Ref(self.public_route_table),
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=Ref(self.internet_gateway),
        ))
    def add_private_route_association(self):
        self.private_route_association = self.template.add_resource(SubnetRouteTableAssociation(
            'PrivateRouteAssociation',
            SubnetId=Ref(self.private_net),
            RouteTableId=Ref(self.private_route_table),
        ))
    def add_nat_eip(self):
        self.nat_eip = self.template.add_resource(EIP(
            'NatEip',
            Domain="vpc",
        ))
    def add_nat_gateway(self):
        self.nat = self.template.add_resource(NatGateway(
            'Nat',
            AllocationId=GetAtt(self.nat_eip, 'AllocationId'),
            SubnetId=Ref(self.public_net),
        ))

    def add_nat_gateway_route(self):
        self.nat_gateway_route = self.template.add_resource(Route(
            'NatRoute',
            RouteTableId=Ref(self.private_route_table),
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=Ref(self.nat),
        ))

    def add_public_net_output(self):
        self.public_net_output = self.template.add_output(Output(
            "PublicSubnet",
            Description="Public subnet network range",
            Value=Ref("PublicSubnet"),
        ))

    def add_private_net_output(self):
        self.private_net_output = self.template.add_output(Output(
            "PrivateSubnet",
            Description="Private subnet network range",
            Value=Ref("PrivateSubnet"),
        ))

    def add_internet_gateway_output(self):
        self.igw_output = self.template.add_output(Output(
            "InternetGateway",
            Description="Internet Gateway",
            Value=Ref(self.internet_gateway),
        ))

    def add_vpc_output(self):
        self.vpc_output = self.template.add_output(Output(
            "VPCId",
            Description="VPCId of vpc",
            Value=Ref("VPC"),
        ))

    def add_nat_eip_output(self):
        self.nat_eip_output = self.template.add_output(Output(
            'NatEip',
            Value=Ref(self.nat_eip),
            Description='Nat Elastic IP',
        ))

def sceptre_handler(sceptre_user_data):
    vpc = Vpc(sceptre_user_data)
    return vpc.template.to_json()
