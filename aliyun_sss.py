#!/usr/bin/env python
# coding=utf-8
import json
import time

import paramiko
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DeleteInstanceRequest import DeleteInstanceRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest
from aliyunsdkecs.request.v20140526.ModifyInstanceAutoReleaseTimeRequest import ModifyInstanceAutoReleaseTimeRequest
from paramiko import SSHException


def runInstance(client, instance_name, password, template_id):
    request = RunInstancesRequest()
    request.set_accept_format('json')
    request.set_InstanceName(instance_name)
    request.set_Password(password)
    request.set_LaunchTemplateId(template_id)
    response = client.do_action_with_exception(request)
    return response


def setAutoRelease(client, instance_id):
    request = ModifyInstanceAutoReleaseTimeRequest()
    request.set_accept_format('json')
    request.set_InstanceId(instance_id)
    request.set_AutoReleaseTime("2019-08-26T14:30:00Z")
    response = client.do_action_with_exception(request)
    return response


def releaseInstance(client, instance_id):
    request = DeleteInstanceRequest()
    request.set_accept_format('json')
    request.set_InstanceId(instance_id)
    request.set_Force(True)
    response = client.do_action_with_exception(request)
    return response


def getInstance(client, instance_name=None, instance_ids=None):
    request = DescribeInstancesRequest()
    request.set_accept_format('json')
    if instance_ids:
        request.set_InstanceIds(instance_ids)
    if instance_name:
        request.set_InstanceName(instance_name)

    response = client.do_action_with_exception(request)
    return response


def installSSS(ip, password):
    transport = paramiko.Transport((ip, 22))
    transport.connect(username='root', password=password)
    ssh_client = paramiko.SSHClient()
    ssh_client._transport = transport
    stdin, stdout, stderr = ssh_client.exec_command('which ssserver||pip install shadowsocks')
    res = stdout.read()
    return res

def runSSS(ip, password):
    transport = paramiko.Transport((ip, 22))
    transport.connect(username='root', password=password)
    ssh_client = paramiko.SSHClient()
    ssh_client._transport = transport
    stdin, stdout, stderr = ssh_client.exec_command('ps -ef |grep ssserver|grep -v grep|| nohup ssserver -s 0.0.0.0 -p 8831 -k 88318831 -m aes-192-cfb -t 600 & \n')
    stdin, stdout, stderr = ssh_client.exec_command('\n')
    res = stdout.read()
    return res

if __name__ == '__main__':
    instance_name = 'sss'
    password = 'P@ssw0rdP@ssw0rd'
    template_id = 'lt-rj93ksthkyhcvihot0wr'

    client = AcsClient('**************', '**************', 'us-west-1')
    res = releaseInstance(client, 'i-rj9hkd156qntz01kvrku')
    instances = getInstance(client, instance_name=instance_name)
    instances_json = json.loads(instances)
    if instances_json['Instances']['Instance']:
        print('InstanceId: {0},PublicIp:{1}'.format(instances_json['Instances']['Instance'][0]['InstanceId'],
                                                    instances_json['Instances']['Instance'][0]['PublicIpAddress'][
                                                        'IpAddress'][0]))
    else:
        res = runInstance(client, instance_name, password, template_id)
        res_json = json.loads(res)
        for i in range(0, 10):
            instance = getInstance(client, instance_ids=res_json['InstanceIdSets']['InstanceIdSet'])
            d = json.loads(instance)
            ins_list = d['Instances']['Instance']
            if ins_list and ins_list[0]['PublicIpAddress']['IpAddress']:
                ip = ins_list[0]['PublicIpAddress']['IpAddress'][0]
                time.sleep(5)
                try:
                    print('[IP:{}] sss installing....'.format(ip))
                    res_install = installSSS(ip, 'P@ssw0rdP@ssw0rd')
                    print('install sss result:{}'.format(res_install))
                    res_run = runSSS(ip, 'P@ssw0rdP@ssw0rd')
                    print('run ssss result:{}'.format(res_run))
                    break
                except SSHException as e:
                    print('[IP:{}] install failed,try again...'.format(ip))
                    continue

                print('InstanceId: {0},PublicIp:{1}'.format(ins_list[0]['InstanceId'],ins_list[0]['PublicIpAddress']['IpAddress'][0]))
            else:
                print('Initing.......wait 5s....')
                time.sleep(5)
        else:
            print('error!!!!!!')
