# coding:utf-8
'''
  author : 9527
'''
from db import DbForUse, DbForRaw
from conf import update_num_per
from validate import validate_asnc


def update_use(proxy_q, validate_q):
    db_use = DbForUse()
    sql = {'score': {'$gte': 0}}
    count = db_use.find(sql).count()
    i = 0
    while count > 0:
        proxies = []
        proxies_db = db_use.find(sql=sql, skip=update_num_per * i, num=update_num_per)
        [proxies.append(proxy) for proxy in proxies_db]
        proxy_q.put_nowait(proxies)
        count -= update_num_per
        i += 1
    proxy_q.put_nowait('end')
    validate_asnc(proxy_q, validate_q)


def update_raw(proxy_q, validate_q):
    db_raw = DbForRaw()
    query = 'left >= 0'
    start = 0
    raw_proxies = db_raw.find(query, start, update_num_per)
    while raw_proxies:
        proxies = []
        [proxies.append(proxy) for proxy in raw_proxies]
        proxy_q.put_nowait(proxies)
        start += update_num_per
        raw_proxies = db_raw.find(query, start, update_num_per)
    proxy_q.put_nowait('over')
    validate_asnc(proxy_q, validate_q)

