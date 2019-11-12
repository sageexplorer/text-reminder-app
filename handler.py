import logging
import uuid
import time 
import boto3
import json 
import os 
import datetime
from datetime import timedelta 
import time 
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
dynamo = boto3.client('dynamodb')

def lambda_handler(event, context):
    '''convert current time into PST '''
    now = datetime.datetime.now() - timedelta(hours=8)
    time_= now.strftime("%Y-%m-%d%H")
    site_url = {YOUR_S3_SITE_URL}

    """
    Check to see the event type: either user generated, or cloudwatch event.
    Only use dynamoDB query if the event source is cloudwatch, and not UI
    Easy way to find out the event type is in the event headers. 
    """
    
    try:
        site_url = event["headers"]["referer"]
    except:
        site_url = None 
    
    if site_url:
        name = str(event["queryStringParameters"]['firstname'])
        message = str(event["queryStringParameters"]['message'])
        phone = str(event["queryStringParameters"]['phone'])
        date = str(event["queryStringParameters"]['date'])
        id = str(uuid.uuid1())
        date_ = date.replace('T', ' ')
        pattern = '%Y-%m-%d %H:%M'
        
        epoch_ = ''.join(date_.split())[:-3]
        
        """ This is current time """
        ts = str(int(datetime.datetime.now().timestamp())-28800)
        print(epoch_)
        """ Add item to the table if the source is not cloudwatch event """
        dynamo.put_item(TableName='iots',Item={'id':{'S':id}, 'time':{'S':epoch_}, 'usr_time':{'S':time_}, 'message':{'S':message}, 'phone':{'S':phone}})
    
        return { 
            'statusCode': 200, 
            'body': 'Thank you for the response' 
        }
    """ if the source doesn't have the right header, then just check the table to see if the record exists """
    else:
  
       table = dynamodb.Table('iots')
       response = table.get_item(Key={'time': time_ })
       try:
           item = response['Item']
           phone = response['Item']['phone']
           message = response['Item']['message']
       except KeyError as error:
           print(error)
           item = None
       except TypeError:
           item = None 
       if item != None:
           print('this will also show up in cloud watch')
           logger.info('got event{}'.format(event))
           sns.publish(PhoneNumber=phone, Message=message)
             
       else:
           print("Something went wrong")
