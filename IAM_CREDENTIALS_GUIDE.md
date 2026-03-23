# IAM Credentials Quick Reference Guide

## Quick Check Commands

### 1. Check if User Exists
```bash
aws iam get-user --user-name drs-agent-installer
```

**Success Output:**
```json
{
    "User": {
        "UserName": "drs-agent-installer",
        "UserId": "AIDAXXXXXXXXXXXXXXXXX",
        "Arn": "arn:aws:iam::sample-accountid:user/drs-agent-installer",
        "CreateDate": "2024-01-15T10:30:00Z"
    }
}
```

**User Doesn't Exist:**
```
An error occurred (NoSuchEntity): The user with name drs-agent-installer cannot be found.
```

---

### 2. Check Attached Policies
```bash
aws iam list-attached-user-policies --user-name drs-agent-installer
```

**Expected Output:**
```json
{
    "AttachedPolicies": [
        {
            "PolicyName": "AWSElasticDisasterRecoveryAgentInstallationPolicy",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSElasticDisasterRecoveryAgentInstallationPolicy"
        }
    ]
}
```

---

### 3. List Access Keys
```bash
aws iam list-access-keys --user-name drs-agent-installer
```

**Output:**
```json
{
    "AccessKeyMetadata": [
        {
            "UserName": "drs-agent-installer",
            "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
            "Status": "Active",
            "CreateDate": "2024-01-15T10:35:00Z"
        }
    ]
}
```

---

### 4. Check Access Key Last Used
```bash
# Replace with your actual access key ID
aws iam get-access-key-last-used --access-key-id AKIAIOSFODNN7EXAMPLE
```

**Output:**
```json
{
    "UserName": "drs-agent-installer",
    "AccessKeyLastUsed": {
        "LastUsedDate": "2024-01-20T14:30:00Z",
        "ServiceName": "drs",
        "Region": "ap-southeast-1"
    }
}
```

---

## Management Commands

### Create User (if doesn't exist)
```bash
aws iam create-user \
  --user-name drs-agent-installer \
  --tags Key=Purpose,Value=DRS-Agent-Installation Key=Service,Value=AWS-DRS
```

### Attach Policy (if not attached)
```bash
aws iam attach-user-policy \
  --user-name drs-agent-installer \
  --policy-arn arn:aws:iam::aws:policy/AWSElasticDisasterRecoveryAgentInstallationPolicy
```

### Create Access Key (if none exists or need new one)
```bash
aws iam create-access-key --user-name drs-agent-installer
```

**IMPORTANT:** Save the output immediately! Secret key is shown only once.

**Output:**
```json
{
    "AccessKey": {
        "UserName": "drs-agent-installer",
        "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
        "Status": "Active",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "CreateDate": "2024-01-20T15:00:00Z"
    }
}
```

### Delete Old Access Key
```bash
# First, list keys to get the AccessKeyId
aws iam list-access-keys --user-name drs-agent-installer

# Then delete specific key
aws iam delete-access-key \
  --user-name drs-agent-installer \
  --access-key-id AKIAIOSFODNN7EXAMPLE
```

---

## Automated Script

### Option 1: Python Script (Recommended)
```bash
python check_iam_credentials.py
```

This script will:
- Check if user exists
- Check if policy is attached
- List existing access keys
- Create new access key if needed
- Save credentials to file

### Option 2: One-Liner Check
```bash
# Check everything at once
echo "=== User ===" && \
aws iam get-user --user-name drs-agent-installer 2>&1 && \
echo -e "\n=== Policies ===" && \
aws iam list-attached-user-policies --user-name drs-agent-installer 2>&1 && \
echo -e "\n=== Access Keys ===" && \
aws iam list-access-keys --user-name drs-agent-installer 2>&1
```

---

## Complete Setup Script

```bash
#!/bin/bash
# Complete IAM setup for DRS agent installation

USER_NAME="drs-agent-installer"
POLICY_ARN="arn:aws:iam::aws:policy/AWSElasticDisasterRecoveryAgentInstallationPolicy"

echo "Checking IAM user: $USER_NAME"

# Check if user exists
if aws iam get-user --user-name $USER_NAME &>/dev/null; then
    echo "User exists"
else
    echo "User doesn't exist. Creating..."
    aws iam create-user --user-name $USER_NAME
    echo "User created"
fi

# Check if policy is attached
if aws iam list-attached-user-policies --user-name $USER_NAME | grep -q "$POLICY_ARN"; then
    echo "Policy attached"
else
    echo "❌ Policy not attached. Attaching..."
    aws iam attach-user-policy --user-name $USER_NAME --policy-arn $POLICY_ARN
    echo "Policy attached"
fi

# List access keys
echo -e "\n=== Access Keys ==="
aws iam list-access-keys --user-name $USER_NAME

# Ask if user wants to create new key
echo -e "\nDo you want to create a new access key? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Creating access key..."
    aws iam create-access-key --user-name $USER_NAME | tee drs-credentials.json
    echo -e "\n Credentials saved to drs-credentials.json"
    echo "   Keep this file secure!"
fi

echo -e "\n Setup complete"
```

**Save as:** `setup_iam_credentials.sh`

**Run:**
```bash
chmod +x setup_iam_credentials.sh
./setup_iam_credentials.sh
```

---

## Security Best Practices

### 1. Rotate Access Keys Regularly
```bash
# Create new key
NEW_KEY=$(aws iam create-access-key --user-name drs-agent-installer)

# Test new key works
# ... update agents with new key ...

# Delete old key
aws iam delete-access-key \
  --user-name drs-agent-installer \
  --access-key-id OLD_KEY_ID
```

### 2. Use IAM Roles Instead (for EC2 instances)
If installing agent on EC2 instances, use IAM role instead:
```bash
# Attach role to EC2 instance
aws ec2 associate-iam-instance-profile \
  --instance-id i-1234567890abcdef0 \
  --iam-instance-profile Name=aws-drs-agent-profile-singapore
```

### 3. Monitor Access Key Usage
```bash
# Check when key was last used
aws iam get-access-key-last-used --access-key-id AKIAIOSFODNN7EXAMPLE

# List all keys and their age
aws iam list-access-keys --user-name drs-agent-installer \
  --query 'AccessKeyMetadata[*].[AccessKeyId,CreateDate,Status]' \
  --output table
```

---

## Troubleshooting

### Error: "User already exists"
```bash
# This is OK! Just check if policy is attached
aws iam list-attached-user-policies --user-name drs-agent-installer
```

### Error: "LimitExceeded: Cannot exceed quota for AccessKeysPerUser: 2"
```bash
# Delete an old key first
aws iam list-access-keys --user-name drs-agent-installer
aws iam delete-access-key --user-name drs-agent-installer --access-key-id OLD_KEY_ID
```

### Error: "Access Denied"
```bash
# Your current IAM user needs these permissions:
# - iam:CreateUser
# - iam:AttachUserPolicy
# - iam:CreateAccessKey
# - iam:ListAccessKeys

# Check your permissions
aws iam get-user
```

### Lost Secret Access Key?
```bash
# You CANNOT retrieve it. You must create a new one:
aws iam create-access-key --user-name drs-agent-installer

# Then delete the old one
aws iam delete-access-key --user-name drs-agent-installer --access-key-id OLD_KEY_ID
```

---

## Quick Status Check

```bash
# Run this to see complete status
cat << 'EOF' > check_status.sh
#!/bin/bash
echo "=== DRS IAM User Status ==="
echo ""
echo "1. User Status:"
aws iam get-user --user-name drs-agent-installer --query 'User.[UserName,Arn,CreateDate]' --output table 2>&1 | head -10

echo ""
echo "2. Attached Policies:"
aws iam list-attached-user-policies --user-name drs-agent-installer --query 'AttachedPolicies[*].PolicyName' --output table 2>&1

echo ""
echo "3. Access Keys:"
aws iam list-access-keys --user-name drs-agent-installer --query 'AccessKeyMetadata[*].[AccessKeyId,Status,CreateDate]' --output table 2>&1

echo ""
echo "=== Status Check Complete ==="
EOF

chmod +x check_status.sh
./check_status.sh
```

---

## Summary

**To check IAM credentials:**
```bash
# Quick check
python check_iam_credentials.py

# OR manual check
aws iam get-user --user-name drs-agent-installer
aws iam list-attached-user-policies --user-name drs-agent-installer
aws iam list-access-keys --user-name drs-agent-installer
```

**To create if missing:**
```bash
# Run the automated script
python check_iam_credentials.py

# OR create manually
aws iam create-user --user-name drs-agent-installer
aws iam attach-user-policy --user-name drs-agent-installer --policy-arn arn:aws:iam::aws:policy/AWSElasticDisasterRecoveryAgentInstallationPolicy
aws iam create-access-key --user-name drs-agent-installer
```
