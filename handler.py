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


dynamodb = boto3.resource('dynamodb')
dynamo = boto3.client('dynamodb')
sns = boto3.client(
    "sns",
    region_name="us-west-2"
)

def lambda_handler(event, context):
    '''convert current time into PST '''
    now = datetime.datetime.now() - timedelta(hours=7)
    time_= now.strftime("%Y-%m-%d%H")
    time_now = now.strftime("%Y-%m-%d%H")
    #site_url = {YOUR_S3_SITE_URL}

    """
    Check to see the event type: either user generated, or cloudwatch event.
    Only use dynamoDB query if the event source is cloudwatch, and not UI
    Easy way to find out the event type is in the event headers. 
    """
    try:
        site_url = event["headers"]["referer"]
    except:
        site_url = None 
    print(event)
    if site_url:
        name = str(event["queryStringParameters"]['firstname'])
        message = str(event["queryStringParameters"]['message'])
        phone = str(event["queryStringParameters"]['phone'])
        date = str(event["queryStringParameters"]['date'])
        date_ = date.replace('T', ' ')
        pattern = '%Y-%m-%d %H:%M'
        epoch_ = ''.join(date_.split())[:-3]
        id = str(uuid.uuid1())
               
        def get_dates(date_):
            time_ = date_
            hour =  time_[-2:]        
            for x in range(1,5):                
                date_time_obj = datetime.datetime.strptime(time_, '%Y-%m-%d%H%f')
                new_date = date_time_obj+ datetime.timedelta(days=1)            
                next_date = new_date.strftime("%Y-%m-%d")        
                next_date_time = next_date + hour 
                time_ = str(next_date_time)
                id = str(uuid.uuid1())
                dynamo.put_item(TableName='iots',Item={'id':{'S':id}, 'time':{'S':time_},'repeat': {'S': repeat}, 'firstname': {'S': name}, 'usr_time':{'S':time_}, 'message':{'S':message}, 'phone':{'S':phone}})
        
        try:
            repeat = str(event["queryStringParameters"]['repeat'])
        except:
            repeat = "none"  

        """ Add item to the table if the source is not cloudwatch event """
        if repeat != 'reccuring':
            dynamo.put_item(TableName='iots',Item={'id':{'S':id}, 'time':{'S':epoch_},'repeat': {'S': repeat}, 'firstname': {'S': name}, 'usr_time':{'S':time_}, 'message':{'S':message}, 'phone':{'S':phone}})
        else:
            get_dates(epoch_)           
        return { 
            'statusCode': 200, 
            'body': 'Thank you for the response' 
        }
     
    else:         
      try:
          table = dynamodb.Table('iots')
          response = table.get_item(Key={'time': epoch_ })
          print(f'MY RESPONSE IS {response}')
          item = response['Item']
          phone = response['Item']['phone']
          message = response['Item']['message']
          table.delete_item(Key={'time': time_now })
      except (KeyError, TypeError) as error:
          print(error)
          item = None

      if item != None:
          print('this will also show up in cloud watch')
     
          sns.publish(PhoneNumber=phone, Message=message)
            
      else:
          print("Something went wrong")
  
