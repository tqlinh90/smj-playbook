import os
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


def createImages(instanceId):
    name = datetime.now().strftime('oq-%Y%m%d-%H%M%S')
    newImageId = awsConnect('ec2').create_image(
        InstanceId=instanceId, Name=name, NoReboot=True,)
    return newImageId['ImageId']


def createLaunchConfig(autoscalingName, oldlc, amiID):
    oname = autoscalingName
    ctime = datetime.now().strftime('%Y%m%d%H%M%S')
    name = "{}-{}".format(oname, ctime)
    blockdevicemapping=[{ "DeviceName": "/dev/xvda", "Ebs": { "VolumeSize": 101 } }]
    if not oldlc:
        print("Not have info from aws launch config")
    elif hasattr(oldlc, 'AssociatePublicIpAddress') and hasattr(oldlc, 'IamInstanceProfile'):
        test = awsConnect('autoscaling').create_launch_configuration(LaunchConfigurationName=name, ImageId=amiID, KeyName=oldlc['KeyName'], SecurityGroups=oldlc['SecurityGroups'], ClassicLinkVPCSecurityGroups=oldlc['ClassicLinkVPCSecurityGroups'], UserData=oldlc[
            'UserData'], InstanceType=oldlc['InstanceType'], BlockDeviceMappings=blockdevicemapping, InstanceMonitoring=oldlc['InstanceMonitoring'],
            IamInstanceProfile=oldlc['IamInstanceProfile'],
            EbsOptimized=oldlc['EbsOptimized'], AssociatePublicIpAddress=oldlc["AssociatePublicIpAddress"])
    elif not hasattr(oldlc, 'AssociatePublicIpAddress') and not hasattr(oldlc, 'IamInstanceProfile'):
        test = awsConnect('autoscaling').create_launch_configuration(LaunchConfigurationName=name, ImageId=amiID, KeyName=oldlc['KeyName'], SecurityGroups=oldlc['SecurityGroups'], ClassicLinkVPCSecurityGroups=oldlc['ClassicLinkVPCSecurityGroups'], UserData=oldlc[
            'UserData'], InstanceType=oldlc['InstanceType'], BlockDeviceMappings=blockdevicemapping, InstanceMonitoring=oldlc['InstanceMonitoring'],
            IamInstanceProfile=oldlc['IamInstanceProfile'],
            EbsOptimized=oldlc['EbsOptimized'],
            # AssociatePublicIpAddress=oldlc["AssociatePublicIpAddress"]
        )
    elif not hasattr(oldlc, 'IamInstanceProfile'):
        test = awsConnect('autoscaling').create_launch_configuration(LaunchConfigurationName=name, ImageId=amiID, KeyName=oldlc['KeyName'], SecurityGroups=oldlc['SecurityGroups'], ClassicLinkVPCSecurityGroups=oldlc['ClassicLinkVPCSecurityGroups'], UserData=oldlc[
            'UserData'], InstanceType=oldlc['InstanceType'], BlockDeviceMappings=blockdevicemapping, InstanceMonitoring=oldlc['InstanceMonitoring'],
            IamInstanceProfile=oldlc['IamInstanceProfile'],
            EbsOptimized=oldlc['EbsOptimized'], AssociatePublicIpAddress=oldlc["AssociatePublicIpAddress"])
    else:
        test = awsConnect('autoscaling').create_launch_configuration(LaunchConfigurationName=name, ImageId=amiID, KeyName=oldlc['KeyName'], SecurityGroups=oldlc['SecurityGroups'], ClassicLinkVPCSecurityGroups=oldlc['ClassicLinkVPCSecurityGroups'], UserData=oldlc[
            'UserData'], InstanceType=oldlc['InstanceType'], BlockDeviceMappings=blockdevicemapping, InstanceMonitoring=oldlc['InstanceMonitoring'],
            IamInstanceProfile=oldlc['IamInstanceProfile'],
            EbsOptimized=oldlc['EbsOptimized'],
            AssociatePublicIpAddress=oldlc["AssociatePublicIpAddress"]
        )
    return name


# count the arguments
arguments = len(sys.argv) - 1

# output argument-wise
position = 1
autoscalingName = []
while (arguments >= position):
    # print("parameter %i: %s" % (position, sys.argv[position]))
    autoscalingName.append(sys.argv[position])
    position = position + 1
print(autoscalingName)
# autoscalingName = sys.argv[1]
for i in autoscalingName:
    response = awsConnect('autoscaling').describe_auto_scaling_groups(
        AutoScalingGroupNames=[i],)
    if not response['AutoScalingGroups']:
        print("Not have info from aws launch config")
    else:
        instanceId = response['AutoScalingGroups'][0]['Instances'][0]['InstanceId']
        print('EC2 id to capture {}'.format(instanceId))
        amiID = createImages(instanceId)
        print('New image amiid {}'.format(amiID))
        lcName = response['AutoScalingGroups'][0]['LaunchConfigurationName']
        print('Existing launch config {}'.format(lcName))

        response = awsConnect('autoscaling').describe_launch_configurations(
            LaunchConfigurationNames=[lcName],)
        existlcConfig = response['LaunchConfigurations'][0]

        newLauchConfig = createLaunchConfig(autoscalingName[0],existlcConfig, amiID)
        print('New launch config {}'.format(newLauchConfig))
        awsConnect('autoscaling').update_auto_scaling_group(
            AutoScalingGroupName=i, LaunchConfigurationName=newLauchConfig)
        print("updated new launch config: {} with ami: {} to AS Ggroup {}".format(
            newLauchConfig, amiID, i))
