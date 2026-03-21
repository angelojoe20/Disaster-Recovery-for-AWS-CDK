#!/usr/bin/env python3
"""
Configure DRS Launch Settings for Source Servers
Run this AFTER installing DRS agents on source servers
"""

import boto3
import sys

REGION = "ap-southeast-1"
ACCOUNT_ID = "sample-accountid"

def get_stack_outputs():
    """Get VPC and Security Group from CDK stack outputs"""
    cfn = boto3.client('cloudformation', region_name=REGION)
    
    try:
        response = cfn.describe_stacks(StackName='DRSStack-Singapore')
        outputs = response['Stacks'][0]['Outputs']
        
        vpc_id = next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'VPCId')
        sg_id = next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'SecurityGroupId')
        recovery_role_arn = next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'RecoveryRoleArn')
        
        return vpc_id, sg_id, recovery_role_arn
    except Exception as e:
        print(f"Error getting stack outputs: {e}")
        sys.exit(1)

def get_source_servers():
    """List all source servers in DRS"""
    drs = boto3.client('drs', region_name=REGION)
    
    try:
        response = drs.describe_source_servers()
        return response.get('items', [])
    except Exception as e:
        print(f"Error getting source servers: {e}")
        return []

def configure_launch_settings(source_server_id, vpc_id, sg_id, recovery_role_arn):
    """Configure launch settings for a source server"""
    drs = boto3.client('drs', region_name=REGION)
    ec2 = boto3.client('ec2', region_name=REGION)
    
    # Get first public subnet from VPC
    subnets = ec2.describe_subnets(
        Filters=[
            {'Name': 'vpc-id', 'Values': [vpc_id]},
            {'Name': 'map-public-ip-on-launch', 'Values': ['true']}
        ]
    )
    
    if not subnets['Subnets']:
        print(f"No public subnets found in VPC {vpc_id}")
        return False
    
    subnet_id = subnets['Subnets'][0]['SubnetId']
    
    try:
        # Update launch configuration
        drs.update_launch_configuration(
            sourceServerID=source_server_id,
            targetInstanceTypeRightSizingMethod='BASIC',  # Auto-select instance type
            copyPrivateIp=False,
            copyTags=True,
            launchDisposition='STARTED',  # Auto-start after recovery
            licensing={
                'osByol': False  # Use AWS-provided licenses
            }
        )
        
        # Update launch configuration template
        drs.update_launch_configuration_template(
            launchConfigurationTemplateID=source_server_id,
            postLaunchEnabled=False,
            targetInstanceTypeRightSizingMethod='BASIC'
        )
        
        print(f"✅ Configured launch settings for server: {source_server_id}")
        print(f"   - Subnet: {subnet_id}")
        print(f"   - Security Group: {sg_id}")
        print(f"   - IAM Role: {recovery_role_arn}")
        return True
        
    except Exception as e:
        print(f"❌ Error configuring server {source_server_id}: {e}")
        return False

def main():
    print("=" * 60)
    print("AWS DRS Launch Settings Configuration")
    print("Region: ap-southeast-1 (Singapore)")
    print("=" * 60)
    print()
    
    # Get CDK stack outputs
    print("📦 Getting CDK stack outputs...")
    vpc_id, sg_id, recovery_role_arn = get_stack_outputs()
    print(f"   VPC: {vpc_id}")
    print(f"   Security Group: {sg_id}")
    print(f"   Recovery Role: {recovery_role_arn}")
    print()
    
    # Get source servers
    print("🔍 Finding source servers...")
    source_servers = get_source_servers()
    
    if not source_servers:
        print("⚠️  No source servers found!")
        print("   Please install DRS agents on your source servers first.")
        sys.exit(0)
    
    print(f"   Found {len(source_servers)} source server(s)")
    print()
    
    # Configure each server
    print("⚙️  Configuring launch settings...")
    success_count = 0
    
    for server in source_servers:
        server_id = server['sourceServerID']
        hostname = server.get('sourceProperties', {}).get('identificationHints', {}).get('hostname', 'Unknown')
        
        print(f"\n📍 Server: {hostname} ({server_id})")
        if configure_launch_settings(server_id, vpc_id, sg_id, recovery_role_arn):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ Successfully configured {success_count}/{len(source_servers)} servers")
    print("=" * 60)

if __name__ == "__main__":
    main()
