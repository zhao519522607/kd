#! /usr/bin/env python

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
import re
import datetime
import docker

client = AcsClient('ackey', 'acs', 'cn-beijing')
request = CommonRequest()
request.set_accept_format('json')
request.set_protocol_type('https') # https | http
request.set_domain('cr.cn-beijing.aliyuncs.com')
request.set_version('2016-06-07')
request.add_header('Content-Type', 'application/json')
exp_imgs = {}

def get_repo():
    request.set_method('GET')
    request.set_uri_pattern('/repos/kdhub')
    request.add_query_param('PageSize', "100")
    body = '''{}'''
    request.set_content(body.encode('utf-8'))

    response = client.do_action_with_exception(request)
    result = json.loads(response)
    repos_list = []
    for n in result['data']['repos']:
        repos_list.append(n['repoName'])
    return repos_list

def get_tags(repo):
    request.set_method('GET')
    request.set_uri_pattern('/repos/kdhub/%s/tags' %repo)
    body = '''{}'''
    request.set_content(body.encode('utf-8'))

    response = client.do_action_with_exception(request)
    result = json.loads(response)
    tag_list = []
    for n in result['data']['tags']:
        if re.search("prod[1-3]?-.*",n['tag']) is not None:
            #print "%s:%s" %(repo,n['tag'])
            tag_list.append(n['tag'])
    exp_imgs[repo] = tag_list

def get_tag(repo,tag):
    request.set_method('GET')
    request.set_uri_pattern('/repos/kdhub/%s/tags/%s' %(repo,tag))
    #request.set_uri_pattern('/repos/kdhub/huiyan-eureka/tags/prod3')
    body = '''{}'''
    request.set_content(body.encode('utf-8'))

    response = client.do_action_with_exception(request)
    print(response)

def del_tag(repo,tag):
    request.set_method('DELETE')
    request.set_uri_pattern('/repos/kdhub/%s/tags/%s' %(repo,tag))
    body = '''{}'''
    request.set_content(body.encode('utf-8'))

    response = client.do_action_with_exception(request)
    print(response)

def compare_time(time1, time2):
    d1 = datetime.datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
    delta = d1 - d2
    if delta.days > 90:
        return True
    else:
        return False

def del_imgs_date():
    repo = get_repo()
    for i in repo:
        get_tags(i)
    t1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for k,v in exp_imgs.items():
        for i in v:
            t2 = i[-15:-5] + " 00:00:00"
            if compare_time(t1,t2):
                #print k + ":" + i
                del_tag(k,i)

def rollback(repo,ver):
    get_tags(repo)
    ver_list = sorted(exp_imgs[repo],reverse=True)
    ver_sub = ver - 1
    ver_name = ver_list[ver_sub]
    img_url = "registry.cn-beijing.aliyuncs.com/kdhub/%s:%s" %(repo,ver_name)
    base_url = img_url[:-16]
    client = docker.from_env()
    client.login(username='用户',password='密码',registry='registry.cn-beijing.aliyuncs.com')
    a = client.images.list()
    if re.search(img_url,str(a)) is None:
        client.api.pull(img_url)
    client.api.tag(img_url,base_url)
    client.api.push(base_url)

if __name__ == '__main__':
    del_imgs_date()
    #rollback('项目名称',1)
    #rollback('项目名称',2)
    #del_tag('项目名称','prod-2020-07-31')
    #get_tags()
    #get_tag()
