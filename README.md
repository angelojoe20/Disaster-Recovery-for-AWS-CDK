# AWS DRS CDK Project - Singapore (ap-southeast-1) Only

AWS CDK project for deploying AWS Elastic Disaster Recovery (DRS) infrastructure in Singapore region.

## ⚠️ IMPORTANT: Region Lock
This stack is **hardcoded to deploy ONLY in Singapore (ap-southeast-1)**. All resources will be created in this region.

## Account Details
- **Account ID**: 345241143078
- **Account**: Stratpoint-Sandbox7-NonProd
- **Region**: ap-southeast-1 (Singapore) - LOCKED

## Prerequisites

1. Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
2. Install [CDK CLI](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_install)
3. Configure AWS CLI credentials
4. Bootstrap CDK in Singapore: `cdk bootstrap aws://345241143078/ap-southeast-1`
5. Initialize DRS in Singapore: `aws drs initialize-service --region ap-southeast-1`
6. Create virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
7. Install dependencies: `pip install -r requirements.txt`

## Deployment

**No environment variables needed!** Region and account are hardcoded.

```bash
cdk deploy
```

## What's Deployed (All in Singapore)

- VPC with public subnets for DRS staging area
- Security group for DRS replication servers (HTTPS only)
- DRS replication configuration template
- IAM roles for DRS service:
  - aws-drs-agent-role-singapore
  - aws-drs-replication-role-singapore
  - aws-drs-recovery-role-singapore

## Communication
- **HTTPS (443) only** - No VPN required
- **Public internet** - Agents connect directly to AWS
- **No inbound ports** - All connections initiated by agents

## Clean Up

```bash
cdk destroy
```

## Documentation
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.