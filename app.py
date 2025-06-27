from flask import Flask, render_template, jsonify, request, Response
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
# Loading the environment variables from the .env file
load_dotenv()
count = 2
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# This file shows how api calls can be made using the web tier and with a database
app = Flask(__name__)

client = boto3.client(
    'sqs',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


@app.route('/')
def home():
    return "Hello World"

@app.route('/face_detection',methods=["POST"])
def face_detection():
#step 1: get the file from the request
    file = request.files['file'].filename
    random_uuid = str(uuid.uuid4())
    

    #step 2: upload the file to s3
    s3_client.upload_fileobj( request.files['file'] , '34294310-in-bucket', random_uuid+file)

    #step 3: send the message to the queue
    payload = {'uuid' : random_uuid, 'file_name' : random_uuid+file}
    client.send_message(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/523955944173/34294310-req-queue',
    MessageBody=json.dumps(payload))
    print("message sent to the request queue")
    #step 4: receive the message from the queue
    while True:
        #step 4a: poll the queue for the message
        response = client.receive_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/523955944173/34294310-resp-queue',
            MaxNumberOfMessages=10,
            VisibilityTimeout=0,
            WaitTimeSeconds=10)
        flag = False
        #step 4b: check if the message is None and if the message is None, sleep for 5 seconds and poll again
        if response == None:
            time.sleep(5)
            continue
        #step 4c: check if the message content is None. It happens when sqs randomly return empty messages in the response., sleep for 5 seconds and poll again
        if response.get('Messages', None) == None:
            time.sleep(5)
            continue
        # step 4d: you have recieved a bunch of messages. Now, check if the message is for the current request based on uuid.
        for msg in response['Messages']:
            body = json.loads(msg['Body'])
            if body['uuid'] == random_uuid:
                flag = True
                print("message received from the response queue", body['result'])
                #step 4e: delete the message from the queue
                del_response = client.delete_message(
                    QueueUrl='https://sqs.us-east-1.amazonaws.com/523955944173/34294310-resp-queue',
                    ReceiptHandle= msg['ReceiptHandle'])
                print("message deleted from the response queue")
                return jsonify({file.split('.')[0]: body['result']})

                    
            


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)