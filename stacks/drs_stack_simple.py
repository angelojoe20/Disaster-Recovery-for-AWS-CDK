import os
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
)
from constructs import Construct

# Fixed configuration for Singapore region only
REGION = "ap-southeast-1"
ACCOUNT_ID = "345241143078"


class DRSStackSimple(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC for DRS staging area (public subnet for HTTPS communication)
        vpc = ec2.Vpc(
            self,
            "DRSVPC-Singapore",
            ip_addresses=ec2.IpAddresses.cidr("10.1.0.0/16"),
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ]
        )

        # Security group for DRS replication servers (HTTPS only)
        sg = ec2.SecurityGroup(
            self,
            "DRSSecurityGroup-Singapore",
            vpc=vpc,
            allow_all_outbound=True,
            description="DRS Replication Security Group - Singapore - HTTPS only",
        )

        # Allow HTTPS outbound to AWS DRS endpoints
        sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="HTTPS to AWS DRS service",
        )

        # Outputs
        CfnOutput(self, "Region", value=REGION, description="Deployment Region")
        CfnOutput(self, "AccountId", value=ACCOUNT_ID, description="AWS Account ID")
        CfnOutput(self, "VPCId", value=vpc.vpc_id, export_name="DRS-VPC-ID-Singapore", description="VPC ID for DRS staging area")
        CfnOutput(self, "SubnetId1", value=vpc.public_subnets[0].subnet_id, export_name="DRS-Subnet-ID-Singapore", description="Subnet ID for DRS staging area")
        CfnOutput(self, "SubnetId2", value=vpc.public_subnets[1].subnet_id, export_name="DRS-Subnet-ID2-Singapore", description="Subnet ID 2 for DRS staging area")
        CfnOutput(self, "SecurityGroupId", value=sg.security_group_id, export_name="DRS-SG-ID-Singapore", description="Security Group ID for DRS replication servers")
        
        # Output command to update DRS replication configuration
        CfnOutput(
            self, 
            "NextSteps",
            value=f"Update DRS replication settings in console to use Subnet: {vpc.public_subnets[0].subnet_id} and Security Group: {sg.security_group_id}",
            description="Next steps after deployment"
        )
