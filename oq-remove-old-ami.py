import os
from re import I
import sys
import json
from dotenv import load_dotenv
import logging
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
load_dotenv()


def awsConnect(service):
    try:
        client = boto3.client(
            service,
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name=os.environ['region'],)
        return client
    except Exception as e:
        print(e)

def getFilterImages(images):
    numbers_images = [i for i in images if i["Name"].startswith("oq-202") ]
    # sorted_images = images #.sort(key=lambda x: x["Name"])
    sorted_images = sorted(numbers_images, key=lambda d: d['Name'], reverse=True)
    remove_lists = sorted_images[IMAGE_KEEP_NUMBER:len(sorted_images)]
    remove_amiid_snapid = []
    for i in remove_lists:
        amiid_snapid = [i['Name'],i['ImageId'],i['BlockDeviceMappings'][0]['Ebs']['SnapshotId']]
        remove_amiid_snapid.append(amiid_snapid)
    return (remove_amiid_snapid)


IMAGE_KEEP_NUMBER=4
response = awsConnect('ec2').describe_images(Owners=['self'])
if not response['Images']:
    print("Not have info from aws launch config")
else:
    Images = response['Images']
    remove_ami_snap = getFilterImages(Images)
    print (remove_ami_snap)
    for ami_id in remove_ami_snap:
        print ("deregister amiid Name {}".format(ami_id[0]))
        awsConnect('ec2').deregister_image(ImageId=ami_id[1])
        print ("delete snapshot {}".format(ami_id[0]))
        awsConnect('ec2').delete_snapshot(SnapshotId=ami_id[2])
© 2022 GitHub, Inc.
Terms
Privacy
Security
Status
Docs
