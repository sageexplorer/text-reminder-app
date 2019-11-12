# text-reminder-app

## This is a simple app that uses AWS Lambda, DynamoDB, Cloudwatch Events, API Gateway, SNS, and S3 to send text message reminder.

## A simple form (index.html) takes input about message, and calls API gateway, which calls Lambda to store record in DynamoDB table.

## A cloudwatch event is triggered every hour to see if there's any record for the hour, and if there is, then SNS send the text message to the phone listed.
