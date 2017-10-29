# coding:utf-8
'''
  author : 9527
'''
from lxml import etree
from util import exist_raw_proxy
from traceback import print_exc


def parse(html, pat):
    if not html: return
    if pat['type'] == 'xpath':
        proxies = parse_xpath(html, pat)
    return proxies


def parse_xpath(html, pat):
    html = html.replace('&#13;', '')
    html = etree.HTML(html)
    trs = html.xpath(pat['match'])
    proxies = set()
    for tr in trs:
        try:
            ip = ''.join(tr.xpath(pat['pos'][0])).strip()
            ip = ip if '.' in ip else ''
            port = ''.join(tr.xpath(pat['pos'][1])).strip()
            port = port if port.isdigit() else ''
            proxy = ip+':'+port
            if not ip or not port or exist_raw_proxy(proxy):
                # print proxy
                continue
            proxies.add(proxy)
        except: print_exc()
    return proxies
