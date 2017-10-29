# coding:utf-8
'''
  author : 9527
'''

import time
from multiprocessing import Process, Queue

from crawl import produce_proxy_asnc
from validate import validate_asnc
from update import update_use, update_raw
from conf import join_max_time
from store import Store
from web import run


def main():
    # 每过一段时间检查一遍代理网站是否发布新的代理并验证可用性
    # 对于可用的代理存入数据库并定时检测是否仍然可用，每个代理最多检测5次
    # 对于所有的代理也定期检查一遍，可用的则存入库中，每个代理最多检测3次
    web_p = Process(target=run)
    web_p.start()
    while True:
        proxy_validate_q = Queue()
        proxy_store_q = Queue()
        validate_q = Queue()
        crawl_p = Process(target=produce_proxy_asnc, args=(proxy_validate_q, proxy_store_q))
        validate_p = Process(target=validate_asnc, args=(proxy_validate_q, validate_q))
        store_p = Process(target=Store, args=(validate_q, proxy_store_q))
        crawl_p.start()
        validate_p.start()
        store_p.start()
        crawl_p.join(join_max_time)
        validate_p.join(join_max_time)
        store_p.join(join_max_time)
        print u'稍后开始更新..'
        time.sleep(60*15)

        # 检测可用代理是否仍然有效
        update_use_p = Process(target=update_use, args=(proxy_validate_q, validate_q))
        update_use_p.start()
        store_use_p = Process(target=Store, args=(validate_q, proxy_validate_q, 'use'))
        store_use_p.start()
        # 检测以前存储的所有代理是否有可用的
        update_raw_p = Process(target=update_raw, args=(proxy_validate_q, validate_q))
        update_raw_p.start()
        start = time.time()
        update_use_p.join(join_max_time)
        end_use = time.time()
        join_time = join_max_time - (end_use - start)
        update_raw_p.join(join_time)
        end_raw = time.time()
        join_time = join_time - (end_raw - end_use)
        store_use_p.join(join_time)
        print 'all update over'
        time.sleep(60)


if __name__ == '__main__':
    main()