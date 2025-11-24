#!/bin/bash

# Ensure the SECRET_NAME environment variable is set
if [ -z "$SECRET_NAME" ]; then
  echo "Environment variable SECRET_NAME is not set."
  exit 1
fi

REGION_NAME="ap-southeast-1"

# Retrieve the secret value using AWS CLI
SECRET_VALUE=$(aws secretsmanager get-secret-value --secret-id $SECRET_NAME --region $REGION_NAME --query SecretString --output text)
echo $SECRET_VALUE
# Check if the secret was retrieved successfully
if [ -z "$SECRET_VALUE" ]; then
  echo "Failed to retrieve secret."
  exit 1
fi

echo "$SECRET_VALUE" | jq -r  '."oauth-private.key"' > oauth-private.key
echo "$SECRET_VALUE" | jq -r  '."oauth-public.key"' > oauth-public.key
