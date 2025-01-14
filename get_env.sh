#!/bin/bash

# Ensure the SECRET_NAME environment variable is set
if [ -z "$SECRET_NAME" ]; then
  echo "Environment variable SECRET_NAME is not set."
  exit 1
fi

REGION_NAME="ap-southeast-1"

# Retrieve the secret value using AWS CLI
SECRET_VALUE=$(aws secretsmanager get-secret-value --secret-id $SECRET_NAME --region $REGION_NAME --query SecretString --output text)

# Check if the secret was retrieved successfully
if [ -z "$SECRET_VALUE" ]; then
  echo "Failed to retrieve secret."
  exit 1
fi

# Convert JSON to .env format
echo "$SECRET_VALUE" | jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' > .env

# Check if the .env file was created successfully
if [ $? -eq 0 ]; then
  echo ".env file created successfully."
else
  echo "Failed to create .env file."
  exit 1
fi
