# coding:utf-8
'''
  author : 9527
'''
from gevent import monkey
monkey.patch_all(thread=False)

import re
import os
import json
import time
import gevent
import traceback
from Queue import Empty
from multiprocessing import Process, Queue, Lock

from db import DbForRaw
from download import download
from util import get_myip, fmt_f, win_kill_p, exist_use_proxy
from conf import proxy_area_url, proxy_type_url, get_ip_url, init_score,\
               greelet_num, validate_p_num, p_max_live, validate_wait_time


lock = Lock()


def validate(proxy, validate_q):
    db_raw = DbForRaw()
    if isinstance(proxy, str):
        type, speed = test_type(proxy)
        if type == -1: return
        area = test_area(proxy) or 'unknown'
        proxy = {
            'ip': proxy,
            'type': type,
            'area': area,
            'time': speed,
            'score': init_score,
            'status': 'new'
        }
        if exist_use_proxy(proxy['ip']): return
    elif isinstance(proxy, tuple):
        proxy, score = proxy
        type, speed = test_type(proxy)
        if type == -1:
            lock.acquire()
            db_raw.update('left='+str(score-1), 'proxy="'+proxy+'"')
            lock.release()
            return
        else:
            area = test_area(proxy) or 'unknown'
            proxy = {
                'ip': proxy,
                'type': type,
                'area': area,
                'time': speed,
                'score': init_score,
                'status': 'new'
            }
            if exist_use_proxy(proxy['ip']):
                lock.acquire()
                db_raw.update('left=' + str(score - 1), 'proxy="' + proxy['ip'] + '"')
                lock.release()
                return
    else:
        ip = proxy['ip']
        type, speed = test_type(ip)
        if type == -1:
            proxy['score'] -= 1
        else:
            proxy['type'] = type
        proxy['time'] = speed
        proxy['status'] = 'old'
        area = proxy['area']
        proxy.pop('_id')
    print str(proxy) + ':' + area
    validate_q.put_nowait(proxy)


def validate_proc(proxies, validate_q, ctrl_q):
    pid = os.getpid()
    print u'进程%s 开始验证这批代理--> %s' % (pid, str(list(proxies)))
    greenlets = []
    for proxy in proxies:
        greenlets.append(gevent.spawn(validate, proxy, validate_q))
        if len(greenlets) >= greelet_num:
            gevent.joinall(greenlets)
            # print u'处理完10个'
            greenlets = []
    gevent.joinall(greenlets)
    ctrl_q.put_nowait(pid)
    print u'进程%s验证完毕，斩!' % pid


# 只有携程还是太慢， 开多进程！
def validate_asnc(proxy_q, validate_q):
    p_s = {}  # 所有进程
    ctrl_q = Queue()
    while True:
        now = time.time()
        for pid, start in p_s.items():
            if now-start >= p_max_live:
                try:
                    win_kill_p(pid)
                except: pass
                print u'进程%s达到最大等待时间,已被斩首！' % pid
                p_s.pop(pid)
        if not ctrl_q.empty():
            end_pid = ctrl_q.get()
            # win_kill_p(end_pid)
            p_s.pop(end_pid)
        try:
            if len(p_s) >= validate_p_num:
                time.sleep(validate_wait_time)
                continue
            proxies = proxy_q.get_nowait()
            if proxies == 'end':
                validate_q.put_nowait('end')
                continue
            if proxies == 'over':
                if p_s:
                    print u'等待验证进程结束..'
                    time.sleep(60)
                    [win_kill_p(pid) for pid in p_s]
                validate_q.put_nowait('over')
                print u'验证完毕，等待存储进程完毕...'
                break
            p = Process(target=validate_proc, args=(proxies, validate_q, ctrl_q))
            p.start()
            p_start = time.time()
            p_s[p.pid] = p_start
        except Empty:
            time.sleep(0.5)
        except Exception, e:
            traceback.print_exc()
            print 'error in validate_asnc:'+str(e)


def test_type(proxy):
    myip = get_myip() or ''
    http_test = 'http://'+proxy_type_url
    https_test = 'https://'+proxy_type_url
    start = time.time()
    http_res = download(http_test, init_time=3, proxy=proxy)
    end_http = time.time()
    https_res = download(https_test, init_time=3, proxy=proxy)
    end_https = time.time()
    status = []
    for res in [http_res, https_res]:
        if not res:
            status.append(False)
            continue
        try:
            data = json.loads(res.content)
            use_proxy = data['headers'].get('Client-Ip', None)
            if not use_proxy:
                origin = data.get('origin', '')
                if origin and myip not in origin: status.append(True)
                else: status.append(False)
            else: status.append(False)
        except: pass
    if not any(status): return -1, -1
    type = 2 if all(status) else 0 if status[0] else 1
    http_time = end_http - start
    https_time = end_https - end_http
    speed = fmt_f((http_time+https_time)/2.0) if type==2 else fmt_f(http_time) if type==0 else fmt_f(https_time)
    return type, speed


def test_area(proxy):
    ip = proxy.split(':')[0]
    res = download(proxy_area_url % ip, init_time=0)
    if res:
        try:
            con = re.search('"location":"(.*?)",', res.content)
            country = con.group(1) if con else None
            if country:
                country = country.split(' ', 1)[0].decode('gbk')
            return country
        except Exception, e:
            print 'error in test_area:'+str(e)+',proxy is:'+proxy
         





# validate('', '')