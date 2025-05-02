import boto3
import os
from datetime import datetime

s3 = boto3.client('s3')
sns = boto3.client('sns')

BUCKET_NAME = os.environ['ngc-collar-data-prod']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
def lambda_handler(event, context):

   today = datetime.now().strftime('%Y-%m-%d')

   success_prefix = "data/payment/archive/success/" + today + "/"
   failure_prefix = "data/payment/archive/failure/" + today + "/"

   success_files = get_files(success_prefix)
   failure_files = get_files(failure_prefix)

   summary = create_summary(success_files, failure_files, today)

   send_email(summary)
   return {
       'statusCode': 200,
       'body': 'Summary email sent successfully.'
   }
def get_files(prefix):
   files = []
   response = s3.list_objects_v2(Bucket=ngc-collar-data-prod, Prefix=prefix)
   if 'Contents' in response:
       for item in response['Contents']:
           filename = item['Key'].split('/')[-1]
           if filename:
               files.append(filename)
   return files
def create_summary(success, failure, date):
   summary = "File Summary for " + date + "\n\n"
   summary += "Success Files (" + str(len(success)) + "):\n"
   if success:
       for file in success:
           summary = summary + "- " + file + "\n"
   else:
       summary += "None\n"
   summary += ("\n"
               "Failure Files (") + str(len(failure)) + "):\n"
   if failure:
       for file in failure:
           summary = summary + "- " + file + "\n"
   else:
       summary += "None"
   return summary
def send_email(message):
   sns.publish(
       TopicArn=SNS_TOPIC_ARN,
       Message=message,
       Subject='S3 File Summary Report'
   )