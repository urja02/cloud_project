import os
import asyncio
import boto3
from dotenv import load_dotenv
import os
import time 
import json
import uuid
import random
import aiobotocore
from aiobotocore.session import get_session


load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
client = boto3.client(
    'sqs',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
   
)

stopped_app_tier = []
running_app_tier = []
ec2 = boto3.client('ec2', region_name='us-east-1', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
ami_id = "ami-0e27ed26b51c775bb"
APP_TIER_DB = ['i-00f9f5e6e87376c3e', 'i-0dec9b4cd15a2c246', 'i-0a265bf559c00389d', 'i-0811b809284c467a7', 'i-0edf338a4f789e578', 'i-07f9e17b8293d2d1b', 'i-0011ac780ffb94795', 'i-0459e7cb3676e03d1', 'i-03d3454ec91b44395', 'i-0c20808157d104026', 'i-01dbe3baf6d48329e', 'i-09b2c7ad271531505', 'i-0979071e42b3a78bd', 'i-0d2ad3ad06b4092f9', 'i-0325e9d5a486ffb11']
APP_TIER_NAME_DB = {}
for i in range(len(APP_TIER_DB)):
    APP_TIER_NAME_DB[APP_TIER_DB[i]] = f'App_Tier_{i+1}'

def get_requests_count():
    response = client.get_queue_attributes(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/523955944173/34294310-req-queue',
            AttributeNames=[
                'ApproximateNumberOfMessages'])
    return int(response['Attributes']['ApproximateNumberOfMessages'])
    
def stopped_app_tier_init():
   
    for instance in range(len(APP_TIER_DB)-1,-1,-1):
        instance_id = APP_TIER_DB[instance]
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
        print(f"Instance {APP_TIER_NAME_DB[instance_id]} is {instance_state}")
        if instance_state == 'running':
            ec2.stop_instances(InstanceIds=[instance_id])
        stopped_app_tier.append(instance_id)
    time.sleep(60)
        
def auto_scale_alg1(requests_count):
    num_instances = 0
    if requests_count <= 15:
        num_instances = requests_count

    elif requests_count > 15:
        num_instances = 15
    num_running_instances = len(running_app_tier)
    return num_instances - num_running_instances
# def get_instances(num_instances, running_app_tier, stopped_app_tier):
def start_instances(num_instances):
    instances_started = 0
    
    while instances_started < num_instances:
        instance_id = stopped_app_tier[-1]
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
        print(f"Instance {APP_TIER_NAME_DB[instance_id]} is {instance_state}")
        
        if instance_state == 'stopped':
            try:
                print(f"Starting instance: {APP_TIER_NAME_DB[instance_id]}")
                ec2.start_instances(InstanceIds=[instance_id])
                # Remove from stopped list and add to running list
                stopped_app_tier.pop()
                running_app_tier.append(instance_id)
                instances_started += 1
                print(f"Successfully started instance: {APP_TIER_NAME_DB[instance_id]}")
            except Exception as e:
                print(f"Failed to start instance {APP_TIER_NAME_DB[instance_id]}: {e}")
                time.sleep(5)
                continue
              # Move to next instance
        elif instance_state == 'running':
            # Instance is already running, move it to running list
            print(f"Instance {APP_TIER_NAME_DB[instance_id]} is already running, moving to running list")
            stopped_app_tier.pop()
            running_app_tier.append(instance_id)
            instances_started += 1
        else:
            # Instance is in some other state (terminating, pending, etc.)
            print(f"Instance {instance_id} is in {instance_state} state, retrying after 10 seconds")
            time.sleep(10)
            

def stop_instances(num_instances):

    for instance in range(num_instances):
        instance_id = running_app_tier.pop()
        ec2.stop_instances(InstanceIds=[instance_id])
        print(f"Stopping instance: {instance_id}")
        stopped_app_tier.append(instance_id)

def run():
    # step 1: populating the stopped_app_tier with the instances and if any instance is running, stop it.
    stopped_app_tier_init()
    count = 0
    while True:
        # step 2: get the number of requests
        requests_count  = get_requests_count()
        print(f"Requests count: {requests_count}")

        if requests_count == 0:
            count += 1
            if count < 2:
                time.sleep(5)
                continue
        count = 0
              

       # step 3: get the number of instances to start or stop
        #if the number of intsances is positive then we scale up.
        #if the number of intsances is negative then we scale down.
        num_instances = auto_scale_alg1(requests_count)
        print(f"Number of instances to start or stop: {num_instances}")
        # step 4: scale up / down
        if num_instances == 0:
            time.sleep(2)
            continue
        elif num_instances > 0:
            print(f"Starting {num_instances} instances")
            start_instances(num_instances)
        elif num_instances < 0:
            print(f"Stopping {abs(num_instances)} instances")
            stop_instances(abs(num_instances))
        # step 5: stop the instances
        
        # step 6: wait for 10 seconds
        time.sleep(5)




        
                

if __name__ == "__main__":
     # Check account limits
    # limits_response = ec2.describe_account_attributes(
    #     AttributeNames=['max-instances']
    # )
    # for attribute in limits_response['AccountAttributes']:
    #     if attribute['AttributeName'] == 'max-instances':
    #         max_instances = attribute['AttributeValues'][0]['AttributeValue']
    #         print(f"Account limit for running instances: {max_instances}")
    #         break
    run()  





        

                