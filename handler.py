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
from utils import Utils

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

        get_frequency = lambda msg: Utils.get_frequency(msg)
        
        
        def get_dates(date_, frequency=None):
     
            time_ = date_
            hour =  time_[-2:]
            
            if frequency == "weekly":
                timetable = [7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84, 91, 98, 105, 112, 119, 126]
            elif frequency == "monthly":
                timetable  = [30, 60,90, 120]
            elif frequency =="reccuring":
                timetable = [x for x in range(30)]
        
            for x in range(1,120):
                
                date_time_obj = datetime.datetime.strptime(time_, '%Y-%m-%d%H%f')
                new_date = date_time_obj+ datetime.timedelta(days=1)
            
                next_date = new_date.strftime("%Y-%m-%d")
        
                next_date_time = next_date + hour 
                time_ = str(next_date_time)
                id = str(uuid.uuid1())
                if x in timetable:
                    dynamo.put_item(TableName='iots',Item={'id':{'S':id}, 'time':{'S':time_},'repeat': {'S': repeat}, 'firstname': {'S': name}, 'usr_time':{'S':time_}, 'message':{'S':message}, 'phone':{'S':phone}})

     
        
        def get_frequency(frequency=None):
            """ This function will take the frequency of the alert, and send the correct value to the dynamoDB table """
            try:
              repeat =  str(event["queryStringParameters"]['repeat'])
              return repeat 
            except:       
                pass 
            try:
                repeat = str(event["queryStringParameters"]['repeat1'])
                return repeat 
            except:
                pass
            try:
              repeat = str(event["queryStringParameters"]['repeat2'])
              return repeat
            except:
                pass 
           
        
        repeat = get_frequency("repeating")    

        """ Add item to the table if the source is not cloudwatch event """
              
        
        if (repeat == "reccuring"):
            dynamo.put_item(TableName='iots',Item={'id':{'S':id}, 'time':{'S':epoch_},'repeat': {'S': repeat}, 'firstname': {'S': name}, 'usr_time':{'S':time_}, 'message':{'S':message}, 'phone':{'S':phone}})
            get_dates(epoch_, "reccuring")
            print("I AM ON THE RECURRING")
        elif (repeat == "weekly"):
            dynamo.put_item(TableName='iots',Item={'id':{'S':id}, 'time':{'S':epoch_},'repeat': {'S': repeat}, 'firstname': {'S': name}, 'usr_time':{'S':time_}, 'message':{'S':message}, 'phone':{'S':phone}})
            get_dates(epoch_, "weekly")
            print("I AM ON THE WEEKLY")
        elif (repeat == "monthly"):
            dynamo.put_item(TableName='iots',Item={'id':{'S':id}, 'time':{'S':epoch_},'repeat': {'S': repeat}, 'firstname': {'S': name}, 'usr_time':{'S':time_}, 'message':{'S':message}, 'phone':{'S':phone}})
            get_dates(epoch_, "monthly")
            print("I AM ON THE MONTHLY")
        else:
            dynamo.put_item(TableName='iots',Item={'id':{'S':id}, 'time':{'S':epoch_},'repeat': {'S': repeat}, 'firstname': {'S': "no rec"}, 'usr_time':{'S':time_}, 'message':{'S':message}, 'phone':{'S':phone}})
             
            
        return { 
            'statusCode': 200, 
            'body': 'Thank you for the response' 
        }
     
    else:
  
       
      try:
          table = dynamodb.Table('iots')
          response = table.get_item(Key={'time': time_now })
          print(response)
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
  
