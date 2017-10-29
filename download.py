# coding:utf-8
'''
  author : 9527
  time : 2017/10/22 16:05
'''
import requests
import traceback
from random import choice

from conf import time_out, try_times, agents


def download(url, init_time=1, proxy=''):
    try:
        headers = {
            'User-Agent': choice(agents)
        }
        if not proxy:
            res = requests.get(url, headers=headers, timeout=time_out)
        else:
            proxies = {
                'http': 'http://'+proxy,
                'https': 'http://'+proxy
            }
            res = requests.get(url, headers=headers, timeout=time_out, proxies=proxies)
        if res.status_code == 200: return res
        raise Exception
    except Exception, e:
        # traceback.print_exc()
        # print 'error in download:'+str(e)
        if init_time < try_times:
            return download(url, init_time + 1, proxy)
        # print 'Max try download %s, still fail!' % url

