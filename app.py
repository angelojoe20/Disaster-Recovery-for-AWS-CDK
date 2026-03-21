#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks import DRSStackSimple

# Fixed region: Singapore (ap-southeast-1)
REGION = "ap-southeast-1"
ACCOUNT = "sample-accountid"

app = cdk.App()
stack = DRSStackSimple(
    app,
    "DRSStack-Singapore",
    env=cdk.Environment(
        account=ACCOUNT,
        region=REGION
    ),
    description="AWS DRS Stack for Singapore (ap-southeast-1) - VPC and Security Group only"
)

cdk.Tags.of(stack).add('created-by', 'cdk')
cdk.Tags.of(stack).add('service', 'drs')
cdk.Tags.of(stack).add('region', 'ap-southeast-1')
cdk.Tags.of(stack).add('account', 'spsandbox7')

app.synth()
