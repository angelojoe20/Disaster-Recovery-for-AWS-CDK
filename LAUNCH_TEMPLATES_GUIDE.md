# AWS DRS Launch Templates & Settings Guide

## Understanding DRS Launch Configurations

### 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ SOURCE SERVER (On-premises/Other Cloud)                     │
│ - Your production server                                    │
│ - DRS Agent installed                                       │
└────────────────┬────────────────────────────────────────────┘
                 │ Continuous Replication (HTTPS/443)
                 ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGING AREA (AWS - Created by CDK)                         │
│ ✅ Replication Configuration Template                       │
│    - Replication servers (t3.small)                         │
│    - EBS volumes for staging                                │
│    - Security groups                                        │
│    - Public subnets                                         │
└────────────────┬────────────────────────────────────────────┘
                 │ EBS Snapshots
                 ↓
┌─────────────────────────────────────────────────────────────┐
│ RECOVERY INSTANCES (During Failover)                        │
│ ⚙️  Launch Settings (Configured per server)                 │
│    - Instance type                                          │
│    - Subnet placement                                       │
│    - Security groups                                        │
│    - IAM roles                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Two Types of Configurations

### 1. Replication Configuration Template (✅ Already in CDK)

**What it controls:** The staging/replication environment

**CDK creates:**
```python
replication_config = drs.CfnReplicationConfigurationTemplate(
    create_public_ip=True,                    # Replication servers get public IPs
    data_plane_routing="PUBLIC_IP",           # Use internet (HTTPS)
    replication_server_instance_type="t3.small",  # Staging server size
    staging_area_subnet_id=vpc.public_subnets[0].subnet_id,  # Where to stage
    replication_servers_security_groups_ids=[sg.security_group_id],  # Firewall
    default_large_staging_disk_type="GP3",    # Storage type
    ebs_encryption="DEFAULT",                 # Encrypt data
)
```

**When it's used:** During continuous replication (24/7)

**Cost:** ~$15-20/month per source server

---

### 2. Launch Settings (❌ Must Configure After Adding Servers)

**What it controls:** The recovered instances during failover

**Must configure:**
- **Instance type** - Size of recovered server (e.g., t3.medium, m5.large)
- **Subnet** - Where to launch (use CDK-created VPC)
- **Security groups** - Firewall rules (use CDK-created SG)
- **IAM role** - Permissions (use CDK-created recovery role)
- **Licensing** - BYOL or AWS-provided
- **Launch disposition** - Auto-start or stopped

**When it's used:** During drill or actual failover

**Cost:** Only during drill/failover (EC2 instance charges)

## 🔧 How to Configure Launch Settings

### Method 1: Automated Script (Recommended)

After deploying CDK and installing agents:

```bash
# Run the configuration script
python configure_launch_settings.py
```

This script will:
1. Find all registered source servers
2. Get VPC/SG/IAM roles from CDK stack
3. Configure launch settings automatically
4. Use right-sizing to match source server specs

### Method 2: AWS Console (Manual)

```
1. Go to AWS DRS Console (Singapore region)
2. Click "Source servers"
3. Select a source server
4. Click "Launch settings" tab
5. Click "Edit"
6. Configure:
   ┌─────────────────────────────────────────────────┐
   │ Instance type right sizing: BASIC               │
   │ Target instance type: (auto-selected)           │
   │ Launch disposition: Started                     │
   │ Copy private IP: No                             │
   │ Copy tags: Yes                                  │
   │ Licensing: Use AWS provided licenses            │
   └─────────────────────────────────────────────────┘
7. Click "Save"
```

### Method 3: AWS CLI

```bash
# Get source server ID
aws drs describe-source-servers --region ap-southeast-1

# Configure launch settings
aws drs update-launch-configuration \
  --source-server-id s-1234567890abcdef0 \
  --target-instance-type-right-sizing-method BASIC \
  --copy-private-ip false \
  --copy-tags true \
  --launch-disposition STARTED \
  --region ap-southeast-1
```

## 🎯 Launch Settings Options Explained

### Instance Type Right Sizing

| Option | Description | Use Case |
|--------|-------------|----------|
| `BASIC` | Matches source server specs | Recommended - maintains performance |
| `NONE` | Manual selection | When you want different size |

### Launch Disposition

| Option | Description | Use Case |
|--------|-------------|----------|
| `STARTED` | Auto-start after recovery | Production failover |
| `STOPPED` | Launch but keep stopped | Testing/validation |

### Licensing

| Option | Description | Cost |
|--------|-------------|------|
| `AWS-provided` | Use AWS licenses | Included in EC2 cost |
| `BYOL` | Bring your own license | You provide license |

## 📊 Complete Deployment Timeline

```
Day 1: Infrastructure Setup
├─ 1. cdk deploy                          (5-10 min) ✅ CDK creates staging
├─ 2. Install DRS agents                  (5 min per server)
└─ 3. Initial replication starts          (2-24 hours)

Day 2: Configuration
├─ 4. Configure launch settings           (5 min) ⚙️ This step!
├─ 5. Verify replication status           (2 min)
└─ 6. Run recovery drill (optional)       (30 min)

Ongoing: Continuous Protection
└─ Continuous replication (24/7)          ✅ DRS fully operational
```

## ✅ Verification Checklist

After configuring launch settings:

```bash
# 1. Check source servers are registered
aws drs describe-source-servers --region ap-southeast-1

# 2. Verify replication status
aws drs describe-source-servers \
  --region ap-southeast-1 \
  --query 'items[*].[sourceServerID,dataReplicationInfo.dataReplicationState]' \
  --output table

# 3. Check launch configuration
aws drs get-launch-configuration \
  --source-server-id s-1234567890abcdef0 \
  --region ap-southeast-1

# 4. Test with recovery drill (optional)
aws drs start-recovery \
  --source-servers sourceServerID=s-1234567890abcdef0 \
  --is-drill true \
  --region ap-southeast-1
```

## 🚨 Common Issues

### Issue 1: "Launch settings not configured"
**Solution:** Run `configure_launch_settings.py` or configure via Console

### Issue 2: "No subnets available"
**Solution:** Ensure CDK stack deployed successfully, check VPC has public subnets

### Issue 3: "IAM role not found"
**Solution:** Verify CDK created recovery role: `aws-drs-recovery-role-singapore`

### Issue 4: "Instance type not available"
**Solution:** Use `BASIC` right-sizing or manually select available instance type

## 💰 Cost Implications

### Staging Area (Always Running)
- Replication servers: ~$15/month per source server
- EBS staging volumes: ~$5-10/month per server
- **Total: ~$20-25/month per protected server**

### Recovery Instances (Only During Drill/Failover)
- EC2 instance: Depends on instance type
- EBS volumes: Depends on size
- **Example: t3.medium = ~$30/month (only when running)**

## 📚 Additional Resources

- [AWS DRS Launch Settings Documentation](https://docs.aws.amazon.com/drs/latest/userguide/launch-settings.html)
- [Instance Right Sizing](https://docs.aws.amazon.com/drs/latest/userguide/right-sizing.html)
- [Recovery Drills](https://docs.aws.amazon.com/drs/latest/userguide/drill-recovery.html)

## 🎯 Summary

**What CDK Does:**
✅ Creates staging infrastructure (replication configuration template)
✅ Creates VPC, subnets, security groups
✅ Creates IAM roles

**What You Must Do:**
⚙️ Install DRS agents on source servers
⚙️ Configure launch settings (use `configure_launch_settings.py`)
⚙️ Run recovery drills to test

**When DRS is Fully Operational:**
✅ Agents installed
✅ Initial replication complete
✅ Launch settings configured
✅ Recovery drill successful
