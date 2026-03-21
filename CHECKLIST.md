# AWS DRS Deployment Checklist

## ✅ Complete Deployment Checklist

### Phase 1: Infrastructure Setup (One-Time)

- [ ] **Install Prerequisites**
  ```bash
  # AWS CLI v2
  # CDK CLI: npm install -g aws-cdk
  # Python 3.8+
  ```

- [ ] **Configure AWS Credentials**
  ```bash
  aws configure
  # Region: ap-southeast-1
  ```

- [ ] **Bootstrap CDK** (One-time per account)
  ```bash
  cdk bootstrap aws://sample-accountid/ap-southeast-1
  ```

- [ ] **Initialize DRS Service** (One-time per region)
  ```bash
  aws drs initialize-service --region ap-southeast-1
  ```

- [ ] **Deploy CDK Stack**
  ```bash
  pip install -r requirements.txt
  cdk deploy
  ```

**Expected Result:** VPC, Security Groups, IAM Roles created in Singapore

---

### Phase 2: Source Server Registration (Per Server)

- [ ] **Verify Source Server Requirements**
  - [ ] Outbound HTTPS (443) allowed
  - [ ] Supported OS (Windows Server 2008+, Linux)
  - [ ] Minimum 2GB RAM
  - [ ] IAM credentials ready

- [ ] **Install DRS Agent - Windows**
  ```powershell
  Invoke-WebRequest -Uri "https://aws-elastic-disaster-recovery-ap-southeast-1.s3.ap-southeast-1.amazonaws.com/latest/windows/AwsReplicationWindowsInstaller.exe" -OutFile "AwsReplicationWindowsInstaller.exe"
  
  .\AwsReplicationWindowsInstaller.exe --region ap-southeast-1 --aws-access-key-id <KEY> --aws-secret-access-key <SECRET>
  ```

- [ ] **Install DRS Agent - Linux**
  ```bash
  wget -O ./aws-replication-installer-init.py https://aws-elastic-disaster-recovery-ap-southeast-1.s3.ap-southeast-1.amazonaws.com/latest/linux/aws-replication-installer-init.py
  
  sudo python3 aws-replication-installer-init.py --region ap-southeast-1 --aws-access-key-id <KEY> --aws-secret-access-key <SECRET>
  ```

- [ ] **Verify Agent Installation**
  ```bash
  aws drs describe-source-servers --region ap-southeast-1
  ```

**Expected Result:** Source servers appear in DRS console with "Initial Sync" status

---

### Phase 3: Launch Settings Configuration (Per Server)

- [ ] **Configure Launch Settings**
  ```bash
  python configure_launch_settings.py
  ```
  
  **OR manually via Console:**
  - [ ] Go to DRS Console → Source servers
  - [ ] Select server → Launch settings
  - [ ] Set instance type (BASIC right-sizing)
  - [ ] Select subnet (from CDK VPC)
  - [ ] Select security group (from CDK)
  - [ ] Set launch disposition (STARTED)
  - [ ] Save settings

- [ ] **Verify Launch Configuration**
  ```bash
  aws drs get-launch-configuration --source-server-id <ID> --region ap-southeast-1
  ```

**Expected Result:** Launch settings configured for each source server

---

### Phase 4: Wait for Initial Replication

- [ ] **Monitor Replication Status**
  ```bash
  aws drs describe-source-servers \
    --region ap-southeast-1 \
    --query 'items[*].[sourceServerID,dataReplicationInfo.dataReplicationState]' \
    --output table
  ```

- [ ] **Wait for "CONTINUOUS" State**
  - Initial sync: 2-24 hours (depends on data size)
  - Status progression: `INITIAL_SYNC` → `CONTINUOUS`

**Expected Result:** All servers show "CONTINUOUS" replication state

---

### Phase 5: Testing (Optional but Recommended)

- [ ] **Run Recovery Drill**
  ```bash
  aws drs start-recovery \
    --source-servers sourceServerID=<ID> \
    --is-drill true \
    --region ap-southeast-1
  ```

- [ ] **Verify Drill Instance**
  - [ ] Check EC2 console for drill instance
  - [ ] Verify instance boots successfully
  - [ ] Test application functionality
  - [ ] Verify network connectivity

- [ ] **Terminate Drill**
  ```bash
  aws drs terminate-recovery-instances \
    --recovery-instance-ids <INSTANCE_ID> \
    --region ap-southeast-1
  ```

**Expected Result:** Successful drill with functional recovery instance

---

## 🎯 DRS is Fully Operational When:

✅ Infrastructure deployed (CDK)
✅ DRS service initialized
✅ Agents installed on all source servers
✅ Launch settings configured
✅ Replication status = "CONTINUOUS"
✅ Recovery drill successful (optional)

---

## 📊 Status Check Commands

### Quick Health Check
```bash
# Count source servers
aws drs describe-source-servers --region ap-southeast-1 --query 'length(items)'

# Check replication status
aws drs describe-source-servers --region ap-southeast-1 \
  --query 'items[*].[sourceProperties.identificationHints.hostname,dataReplicationInfo.dataReplicationState]' \
  --output table

# Check last snapshot time
aws drs describe-source-servers --region ap-southeast-1 \
  --query 'items[*].[sourceProperties.identificationHints.hostname,dataReplicationInfo.lagDuration]' \
  --output table
```

### Detailed Server Info
```bash
# Get specific server details
aws drs describe-source-servers \
  --filters sourceServerIDs=<ID> \
  --region ap-southeast-1

# Check recovery readiness
aws drs get-replication-configuration \
  --source-server-id <ID> \
  --region ap-southeast-1
```

---

## 🚨 Troubleshooting Checklist

### Agent Won't Connect
- [ ] Check outbound HTTPS (443) is allowed
- [ ] Verify IAM credentials are correct
- [ ] Confirm using ap-southeast-1 region
- [ ] Check DRS service is initialized
- [ ] Review agent logs on source server

### Replication Stuck at "Initial Sync"
- [ ] Check network bandwidth
- [ ] Verify sufficient disk space on source
- [ ] Check CloudWatch logs for errors
- [ ] Ensure replication servers are running

### Launch Settings Not Saving
- [ ] Verify source server is registered
- [ ] Check IAM permissions
- [ ] Ensure VPC/subnet/SG exist
- [ ] Try via Console instead of CLI

### Recovery Drill Fails
- [ ] Verify launch settings configured
- [ ] Check subnet has available IPs
- [ ] Verify security group rules
- [ ] Check IAM recovery role attached

---

## 💰 Cost Tracking

### Monthly Costs (Per Server)
- Replication server: ~$15/month
- Staging EBS volumes: ~$5-10/month
- **Total per server: ~$20-25/month**

### Drill/Failover Costs (Only When Running)
- Recovery EC2 instance: Varies by type
- Recovery EBS volumes: Varies by size
- Data transfer: Minimal

### Cost Optimization
- [ ] Use t3.small for replication servers ✅ (already configured)
- [ ] Use GP3 for staging disks ✅ (already configured)
- [ ] Terminate drill instances after testing
- [ ] Monitor unused source servers

---

## 📞 Support Resources

- **AWS DRS Documentation**: https://docs.aws.amazon.com/drs/
- **AWS Support**: Open ticket in Console
- **CDK Issues**: Check CloudFormation events
- **Agent Issues**: Check `/var/log/aws-replication-agent/` (Linux) or Event Viewer (Windows)

---

## 🔄 Regular Maintenance

### Weekly
- [ ] Check replication lag
- [ ] Verify all servers in "CONTINUOUS" state
- [ ] Review CloudWatch metrics

### Monthly
- [ ] Run recovery drill
- [ ] Review and optimize costs
- [ ] Update launch settings if needed
- [ ] Check for agent updates

### Quarterly
- [ ] Full disaster recovery test
- [ ] Review and update runbooks
- [ ] Validate RTO/RPO metrics
- [ ] Audit IAM permissions
