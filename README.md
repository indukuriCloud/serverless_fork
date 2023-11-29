# Lambda Function: GitHub Release Downloader

This AWS Lambda function downloads a GitHub release archive from a specified repository URL and uploads it to Google Cloud Storage. It also sends email notifications using Mailgun and tracks the email status in AWS DynamoDB.

## Overview

The Lambda function is triggered by an event published to an Amazon SNS topic. The SNS message includes details such as the GitHub repository URL, user information, and assignment details.

## Functionality

1. **Download Release:** Downloads a GitHub release archive using the provided repository URL.
2. **Upload to GCS:** Uploads the downloaded file to Google Cloud Storage (GCS).
3. **Email Notification:** Sends an email notification about the download status using Mailgun.
4. **Email Tracking:** Tracks the sent emails in AWS DynamoDB.

## Configuration

Before deploying the Lambda function, ensure you have configured the following environment variables:

- **GCS_BUCKET_NAME:** Name of the Google Cloud Storage bucket.
- **GCP_CREDENTIALS:** Base64-encoded JSON credentials for GCP service account.
- **MAILGUN_API_KEY:** API key for Mailgun.
- **MAILGUN_DOMAIN:** Domain associated with your Mailgun account.
- **MAILGUN_SENDER:** Sender email address for Mailgun.
- **DYNAMODB_TABLE:** Name of the DynamoDB table for tracking emails.
- **AWS_REG:** AWS region for DynamoDB.

## How to Use

1. **Deploy the Lambda Function:**
   - Deploy the Lambda function using the provided code.
   - Subscribe the Lambda function to the appropriate SNS topic.

2. **Send SNS Event:**
   - Send an SNS event with details about the GitHub repository using the provided schema.

3. **Monitor Logs:**
   - Monitor the CloudWatch Logs for the Lambda function to view execution logs.