# coding:utf-8
'''
  author : 9527
  time : 2017/10/23 10:18
'''
import sys
reload(sys)
sys.setdefaultencoding('gbk')
import json
from subprocess import check_output

from download import download
from conf import get_ip_url
from db import DbForRaw, DbForUse


def get_myip():
    res = download(get_ip_url)
    if res:
        con = json.loads(res.content)
        return con.get('origin', '')


def exist_raw_proxy(proxy):
    db_raw = DbForRaw()
    res = db_raw.find('proxy="'+proxy+'"')
    return len(res) > 0


def exist_use_proxy(proxy):
    db_use = DbForUse()
    return db_use.find({'ip': proxy}).count() > 0


def fmt_f(num):
    return round(num, 3)


def win_kill_p(pid):
    try:
        f = open('error.txt', 'w')
        check_output('taskkill /f /pid %s' % pid, stderr=f)
    except: pass







