
import boto3

# Let's use Amazon S3
s3 = boto3.resource('s3')


# Upload a new file
data = open('facerec-master.zip', 'rb')
s3.Bucket('hoosthere-bucket').put_object(Key='facerec-master.zip', Body=data, ACL='public-read')