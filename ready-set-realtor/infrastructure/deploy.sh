#!/bin/bash

# Exit on error
set -e

# Load environment variables
source .env

# Check required environment variables
required_vars=(
    "AWS_PROFILE"
    "AWS_REGION"
    "ENVIRONMENT"
    "DOMAIN_NAME"
    "CERTIFICATE_ARN"
    "DB_USERNAME"
    "DB_PASSWORD"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Required environment variable $var is not set"
        exit 1
    fi
done

# Create S3 bucket for CloudFormation templates
aws s3 mb s3://ready-set-realtor-cfn-templates --region $AWS_REGION || true

# Package and upload CloudFormation templates
aws cloudformation package \
    --template-file vpc.yml \
    --s3-bucket ready-set-realtor-cfn-templates \
    --output-template-file vpc-packaged.yml

aws cloudformation package \
    --template-file rds.yml \
    --s3-bucket ready-set-realtor-cfn-templates \
    --output-template-file rds-packaged.yml

aws cloudformation package \
    --template-file s3-cloudfront.yml \
    --s3-bucket ready-set-realtor-cfn-templates \
    --output-template-file s3-cloudfront-packaged.yml

# Deploy VPC stack
echo "Deploying VPC stack..."
aws cloudformation deploy \
    --template-file vpc-packaged.yml \
    --stack-name ready-set-realtor-vpc-$ENVIRONMENT \
    --parameter-overrides \
        EnvironmentName=$ENVIRONMENT \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset

# Get VPC outputs
VPC_ID=$(aws cloudformation describe-stacks \
    --stack-name ready-set-realtor-vpc-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`VPC`].OutputValue' \
    --output text)

PRIVATE_SUBNET_1=$(aws cloudformation describe-stacks \
    --stack-name ready-set-realtor-vpc-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnet1`].OutputValue' \
    --output text)

PRIVATE_SUBNET_2=$(aws cloudformation describe-stacks \
    --stack-name ready-set-realtor-vpc-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnet2`].OutputValue' \
    --output text)

# Deploy RDS stack
echo "Deploying RDS stack..."
aws cloudformation deploy \
    --template-file rds-packaged.yml \
    --stack-name ready-set-realtor-rds-$ENVIRONMENT \
    --parameter-overrides \
        VpcId=$VPC_ID \
        PrivateSubnet1=$PRIVATE_SUBNET_1 \
        PrivateSubnet2=$PRIVATE_SUBNET_2 \
        DBUsername=$DB_USERNAME \
        DBPassword=$DB_PASSWORD \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset

# Deploy S3 and CloudFront stack
echo "Deploying S3 and CloudFront stack..."
aws cloudformation deploy \
    --template-file s3-cloudfront-packaged.yml \
    --stack-name ready-set-realtor-frontend-$ENVIRONMENT \
    --parameter-overrides \
        DomainName=$DOMAIN_NAME \
        CertificateArn=$CERTIFICATE_ARN \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset

# Get CloudFront distribution ID
CLOUDFRONT_DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
    --stack-name ready-set-realtor-frontend-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
    --output text)

# Update GitHub repository secrets
if [ ! -z "$GITHUB_TOKEN" ]; then
    echo "Updating GitHub repository secrets..."
    
    # Get RDS endpoint
    DB_ENDPOINT=$(aws cloudformation describe-stacks \
        --stack-name ready-set-realtor-rds-$ENVIRONMENT \
        --query 'Stacks[0].Outputs[?OutputKey==`DBEndpoint`].OutputValue' \
        --output text)
    
    # Update secrets using GitHub CLI
    gh secret set AWS_ACCESS_KEY_ID --body "$AWS_ACCESS_KEY_ID"
    gh secret set AWS_SECRET_ACCESS_KEY --body "$AWS_SECRET_ACCESS_KEY"
    gh secret set AWS_REGION --body "$AWS_REGION"
    gh secret set CLOUDFRONT_DISTRIBUTION_ID --body "$CLOUDFRONT_DISTRIBUTION_ID"
    gh secret set DATABASE_URL --body "postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_ENDPOINT:5432/ready_set_realtor"
    gh secret set NEXT_PUBLIC_API_URL --body "https://api.$DOMAIN_NAME"
fi

echo "Deployment completed successfully!" 