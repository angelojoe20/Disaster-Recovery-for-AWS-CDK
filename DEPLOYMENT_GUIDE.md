# AWS DRS Deployment Guide - Singapore (ap-southeast-1) ONLY

## ⚠️ IMPORTANT: This stack is LOCKED to Singapore region (ap-southeast-1)

## Account Information
- **Account ID**: sample-accountid
- **Account Name**: sandbox-environment
- **Region**: ap-southeast-1 (Singapore) - HARDCODED

## Architecture
- **Communication**: HTTPS (port 443) over public internet
- **No VPN required**: DRS agents communicate directly with AWS endpoints
- **Public subnets**: Replication servers use public IPs
- **Region**: Singapore (ap-southeast-1) ONLY

## Prerequisites

1. **Install AWS CLI and CDK**
   ```bash
   # Install AWS CLI v2
   # Install CDK: npm install -g aws-cdk
   ```

2. **Configure AWS credentials for Singapore**
   ```bash
   aws configure
   # Enter your access key, secret key
   # Default region: ap-southeast-1
   ```

3. **Bootstrap CDK in Singapore** (one-time)
   ```bash
   cdk bootstrap aws://sample-accountid/ap-southeast-1
   ```

4. **Initialize DRS Service in Singapore** (one-time)
   ```bash
   aws drs initialize-service --region ap-southeast-1
   ```

## Deployment Steps

### 1. NO Environment Variables Needed!
The region and account are hardcoded in the stack.

### 2. Install Python Dependencies
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 3. Deploy CDK Stack (Singapore Only)
```bash
# Bootstrap (one-time)
cdk bootstrap aws://345241143078/ap-southeast-1

# Preview CloudFormation template
cdk synth

# Deploy to Singapore (ap-southeast-1)
cdk deploy
```

### 4. Configure DRS Replication Template
```bash
# After CDK deployment completes, run:
python setup_drs_replication.py

# This creates the DRS replication configuration using the VPC/subnet/SG from CDK
```

## Install DRS Agent on Source Servers

### For Windows Source Servers:
```powershell
# Download agent (Singapore region)
Invoke-WebRequest -Uri "https://aws-elastic-disaster-recovery-ap-southeast-1.s3.ap-southeast-1.amazonaws.com/latest/windows/AwsReplicationWindowsInstaller.exe" -OutFile "AwsReplicationWindowsInstaller.exe"

# Install agent
.\AwsReplicationWindowsInstaller.exe --region ap-southeast-1 --aws-access-key-id <KEY> --aws-secret-access-key <SECRET>
```

### For Linux Source Servers:
```bash
# Download and install (Singapore region)
wget -O ./aws-replication-installer-init.py https://aws-elastic-disaster-recovery-ap-southeast-1.s3.ap-southeast-1.amazonaws.com/latest/linux/aws-replication-installer-init.py

sudo python3 aws-replication-installer-init.py --region ap-southeast-1 --aws-access-key-id <KEY> --aws-secret-access-key <SECRET>
```

## Network Requirements

### Source Servers Must Allow Outbound:
- **Port 443 (HTTPS)** to AWS DRS endpoints in Singapore
- **Port 443 (HTTPS)** to AWS S3 endpoints in Singapore
- **Port 443 (HTTPS)** to AWS API endpoints in Singapore

### No Inbound Ports Required!

### AWS Endpoints Used (via HTTPS) - Singapore:
- `drs.ap-southeast-1.amazonaws.com`
- `s3.ap-southeast-1.amazonaws.com`
- `ec2.ap-southeast-1.amazonaws.com`

## Verify Deployment

```bash
# Check DRS service status (Singapore)
aws drs describe-source-servers --region ap-southeast-1

# Check replication status
aws drs describe-jobs --region ap-southeast-1

# List replication configuration
aws drs describe-replication-configuration-templates --region ap-southeast-1
```

## Resources Created (All in Singapore)

- VPC: `10.1.0.0/16` with 2 public subnets
- Security Group: HTTPS (443) outbound only
- IAM Roles:
  - `aws-drs-agent-role-singapore`
  - `aws-drs-replication-role-singapore`
  - `aws-drs-recovery-role-singapore`
- DRS Replication Configuration Template

## Cost Estimate (Singapore Region)
- **Per source server**: ~$20-25/month
- **Replication servers**: t3.small (~$15/month each)
- **EBS volumes**: GP3 storage costs
- **Data transfer**: Outbound data charges

## Clean Up
```bash
# Remove source servers first (via Console/CLI)
aws drs disconnect-from-service --source-server-id <id> --region ap-southeast-1

# Then destroy CDK stack
cdk destroy
```

## Troubleshooting

### Agent Can't Connect:
1. Check outbound HTTPS (443) is allowed
2. Verify IAM credentials have correct permissions
3. Check security group allows outbound to 0.0.0.0/0:443
4. Confirm using Singapore region (ap-southeast-1)

### Replication Not Starting:
1. Verify DRS service is initialized in Singapore
2. Check agent role has required policies
3. Review CloudWatch logs in Singapore region

### Wrong Region Error:
- This stack ONLY deploys to Singapore (ap-southeast-1)
- All resources are locked to this region
- Cannot deploy to other regions

## Support
- AWS DRS Documentation: https://docs.aws.amazon.com/drs/
- AWS Support: Open ticket in AWS Console
