import os
import json
import subprocess
import requests
import time
from boto3 import resource
import logging
from google.cloud import storage
import base64

logger = logging.getLogger("lambda")

def lambda_handler(event, context):
    try:
        # Extract necessary information from the SNS event
        sns_message = json.loads(event['Records'][0]['Sns']['Message'])
        repo_url = sns_message['repo_url']
        user_id = sns_message['user_id']
        assigmment_id = sns_message['assigmment_id']
        submission_id = sns_message['submission_id']
        user_email = sns_message['user_email']

        # Download the release from GitHub
        download_path = '/tmp/{}/{}'.format(user_id, assigmment_id)
        download_release(repo_url, download_path, user_email, user_id, assigmment_id, submission_id)
    except Exception as e:
        logger.error("Error while handling data : {}".format(str(e)))

def download_release(repo_url, download_path, user_email, user_id, assigmment_id, submission_id):
    
    try:
        
        response = requests.get(repo_url)
        content_type = response.headers.get('content-type')
    
        print(content_type)
        print(response.headers.get("Content-Length"))
        if response.headers.get("Content-Length"):
            if 'application/zip' in content_type:
                if not os.path.exists(download_path):
                    os.makedirs(download_path)
                with open('/tmp/{}/{}/{}.zip'.format(user_id, assigmment_id, submission_id), "wb") as local_file:
                    local_file.write(response.content)

                upload_to_gcs('{}/{}/{}.zip'.format(user_id, assigmment_id, submission_id), os.getenv("GCS_BUCKET_NAME"))
                email_status(user_email, "You file has been downloaded successfully for submission: {}".format(submission_id))
                
            else:
                email_status(user_email, "Incorrect file format, Please upload the URL of zip")
        else:
            email_status(user_email, "Invalid or unauthorized URL")

                
    except Exception as e:
        logger.error("Error while Downloading data : {}".format(str(e)))

def upload_to_gcs(file_path, bucket_name):

    try:
        
        json_credentials = json.loads(base64.b64decode(os.getenv("GCP_CREDENTIALS")))

        # Specify the file path where you want to save the JSON file
        gcp_creds = '/tmp/cred.json'

        # Write the JSON data to a file
        with open(gcp_creds, 'w') as json_file:
            json.dump(json_credentials, json_file, indent=2)

        client = storage.Client.from_service_account_json(gcp_creds)
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(file_path)

        blob.upload_from_filename("/tmp/{}".format(file_path))

    except Exception as e:
        logger.error("Error while uploading files to GCS : {}".format(str(e)))

def email_status(user_email, message):
        
    try:
        # Your Mailgun API key and domain
        mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        mailgun_domain = os.getenv("MAILGUN_DOMAIN")

        # Mailgun sender email address
        sender = os.getenv("MAILGUN_SENDER")

        # Mailgun API endpoint for sending emails
        mailgun_api_url = f'https://api.mailgun.net/v3/{mailgun_domain}/messages'

        subject = 'Download Status Notification'
        body_text = 'The status of your download is:\n\n {} \n\n Thanks,\nManohar Varma'.format(message)


        # Create the API request
        response = requests.post(
            mailgun_api_url,
            auth=('api', mailgun_api_key),
            data={
                'from': f'{sender}',
                'to': f'{user_email}',
                'subject': subject,
                'text': body_text
            }
        )

        # Check if the email was sent successfully
        if response.status_code == 200:
            print(f'Email sent successfully to {user_email}')
        else:
            print(f'Failed to send email. Status code: {response.status_code}')

        track_email(os.getenv("DYNAMODB_TABLE"), user_email, body_text)
    except Exception as e:
        logger.error("Error while sending email : {}".format(str(e)))

def track_email(table_name, user_email, message):
    try:
        # Use AWS DynamoDB to track emails sent
        dynamodb = resource('dynamodb', region_name=os.getenv("AWS_REG"))
        table = dynamodb.Table(table_name)

        item_id = str(int(time.time()))

        table.put_item(
            Item={
                'id': int(item_id),
                'UserEmail': user_email,
                'Timestamp': str(time.time()),
                'Mesaage': message
            }
        )
    except Exception as e:
        logger.error("Error while tracking mail : {}".format(str(e)))
        
# data = {
#   "repo_url": "https://github.com/indukuriCloud/test/raw/main/terraform.zip",
#   "user_id": "123",
#   "assigmment_id": "123",
#   "submission_id": "1wewe3",
#   "user_email": "i.vaibhavmahajan@gmail.com"
# }
# lambda_handler(data, "ee")