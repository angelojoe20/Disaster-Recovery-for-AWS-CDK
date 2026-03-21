#!/usr/bin/env python3
"""
Configure DRS Replication Configuration Template
Run this AFTER CDK stack deployment
"""

import boto3
import sys
import json

REGION = "ap-southeast-1"
STACK_NAME = "DRSStack-Singapore"

def get_stack_outputs():
    """Get outputs from CDK stack"""
    cfn = boto3.client('cloudformation', region_name=REGION)
    
    try:
        response = cfn.describe_stacks(StackName=STACK_NAME)
        outputs = response['Stacks'][0]['Outputs']
        
        output_dict = {}
        for output in outputs:
            output_dict[output['OutputKey']] = output['OutputValue']
        
        return output_dict
    except Exception as e:
        print(f"❌ Error getting stack outputs: {e}")
        print(f"   Make sure CDK stack '{STACK_NAME}' is deployed")
        sys.exit(1)

def check_existing_template():
    """Check if replication configuration template already exists"""
    drs = boto3.client('drs', region_name=REGION)
    
    try:
        response = drs.describe_replication_configuration_templates()
        templates = response.get('items', [])
        
        if templates:
            print(f"✓ Found existing replication configuration template")
            template = templates[0]
            template_id = template['replicationConfigurationTemplateID']
            print(f"   Template ID: {template_id}")
            print(f"   Current Subnet: {template.get('stagingAreaSubnetId', 'N/A')}")
            print(f"   Current Security Groups: {template.get('replicationServersSecurityGroupsIDs', [])}")
            return template_id
        
        return None
    except Exception as e:
        print(f"❌ Error checking existing templates: {e}")
        return None

def update_replication_config(template_id, subnet_id, sg_id):
    """Update existing DRS replication configuration template"""
    drs = boto3.client('drs', region_name=REGION)
    
    try:
        response = drs.update_replication_configuration_template(
            replicationConfigurationTemplateID=template_id,
            associateDefaultSecurityGroup=False,
            bandwidthThrottling=0,
            createPublicIP=True,
            dataPlaneRouting='PUBLIC_IP',
            defaultLargeStagingDiskType='GP3',
            ebsEncryption='DEFAULT',
            pitPolicy=[
                {
                    'enabled': True,
                    'interval': 10,
                    'retentionDuration': 60,
                    'ruleID': 1,
                    'units': 'MINUTE'
                },
                {
                    'enabled': True,
                    'interval': 1,
                    'retentionDuration': 24,
                    'ruleID': 2,
                    'units': 'HOUR'
                },
                {
                    'enabled': True,
                    'interval': 1,
                    'retentionDuration': 7,
                    'ruleID': 3,
                    'units': 'DAY'
                }
            ],
            replicationServerInstanceType='t3.small',
            replicationServersSecurityGroupsIDs=[sg_id],
            stagingAreaSubnetId=subnet_id,
            stagingAreaTags={
                'Name': 'DRS-Staging-Singapore',
                'Service': 'DRS',
                'Region': 'ap-southeast-1',
                'ManagedBy': 'CDK'
            },
            useDedicatedReplicationServer=False
        )
        
        print(f"\n✅ Successfully updated DRS replication configuration template")
        print(f"   Template ID: {template_id}")
        print(f"   Subnet: {subnet_id}")
        print(f"   Security Group: {sg_id}")
        print(f"   Instance Type: t3.small")
        print(f"   Data Routing: PUBLIC_IP (HTTPS)")
        
        return template_id
    except Exception as e:
        print(f"❌ Error updating replication configuration: {e}")
        return None

def main():
    print("=" * 70)
    print("AWS DRS Replication Configuration Setup")
    print("Region: ap-southeast-1 (Singapore)")
    print("=" * 70)
    print()
    
    # Step 1: Get stack outputs
    print("Step 1: Getting CDK stack outputs...")
    outputs = get_stack_outputs()
    
    subnet_id = outputs.get('SubnetId1')  # Use first subnet
    sg_id = outputs.get('SecurityGroupId')
    vpc_id = outputs.get('VPCId')
    
    if not subnet_id or not sg_id:
        print("❌ Required outputs not found in stack")
        sys.exit(1)
    
    print(f"   VPC ID: {vpc_id}")
    print(f"   Subnet ID: {subnet_id}")
    print(f"   Security Group ID: {sg_id}")
    print()
    
    # Step 2: Check existing templates
    print("Step 2: Checking for existing replication configuration...")
    template_id = check_existing_template()
    print()
    
    # Step 3: Update replication configuration
    print("Step 3: Updating DRS replication configuration template...")
    result = update_replication_config(template_id, subnet_id, sg_id)
    
    if not result:
        sys.exit(1)
    
    print()
    print("=" * 70)
    print("✅ DRS Replication Configuration Complete")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("1. Install DRS agents on source servers")
    print("2. Configure launch settings for each server")
    print("3. Wait for initial replication to complete")
    print()
    print("Commands:")
    print(f"  # Install agent (Windows):")
    print(f"  .\\AwsReplicationWindowsInstaller.exe --region {REGION} --aws-access-key-id <KEY> --aws-secret-access-key <SECRET>")
    print()
    print(f"  # Verify source servers:")
    print(f"  aws drs describe-source-servers --region {REGION}")
    print()
    print(f"  # Configure launch settings:")
    print(f"  python configure_launch_settings.py")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
