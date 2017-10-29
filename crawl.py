# coding:utf-8
'''
  author : 9527
'''
from gevent import monkey
monkey.patch_all(thread=False)

import gevent
from time import sleep

from conf import url_pats, greelet_num
from download import download
from parse import parse


def produce_proxy(url, pat, proxy_validate_q, proxy_store_q):
    res = download(url)
    if not res: return
    proxies = parse(res.content, pat)
    if proxies:
        proxy_validate_q.put_nowait(proxies)
        proxy_store_q.put_nowait(proxies)
    sleep(3)


def produce_proxy_asnc(proxy_validate_q, proxy_store_q):
    for url_pat in url_pats:
        pat = url_pat['pat']
        greenlets = []
        for url in url_pat['urls']:
            # produce_proxy(url, pat, proxy_validate_q, proxy_store_q)
            greenlets.append(gevent.spawn(produce_proxy, url, pat, proxy_validate_q, proxy_store_q))
            if len(greenlets) >= greelet_num:
                gevent.joinall(greenlets)
                greenlets = []
        gevent.joinall(greenlets)
    proxy_validate_q.put_nowait('over')
    proxy_store_q.put_nowait('end')


# from Queue import Queue
# if __name__ == '__main__':
#     proxy_q = Queue()
#     produce_proxy_asnc(proxy_q)

