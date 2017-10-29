# coding:utf-8
'''
  author : 9527
'''
import traceback

from time import sleep
from Queue import Empty
from threading import Thread

from conf import store_num_per, raw_init_score
from db import DbForUse, DbForRaw


class Store(object):
    def __init__(self, validate_q, proxy_raw_q, store_type=None):
        self.validate_q = validate_q
        self.proxy_q = proxy_raw_q
        self.raw_num = 1
        self.use_num = 0
        self.update_num = 1
        self.update_can_use_num = 0
        if store_type == 'use': self.store_use()
        elif store_type == 'raw': self.store_raw()
        else: self.store()

    def store_use(self):
        db = DbForUse()
        data = []
        while True:
            try:
                proxy = self.validate_q.get_nowait()
                if proxy == 'end':
                    print 'update over, still can use num is:' + str(self.update_can_use_num)
                    print u'本次更新后的可用率：%.2f%%' % (self.update_can_use_num / float(self.update_num) * 100)
                    continue
                if proxy == 'over':
                    if data:
                        db.insert_many(data)
                        self.use_num += len(data)
                    print u"本次store_use over, useful proxy's num is:" + str(self.use_num)
                    sum = db.find().count()
                    print u'总有用代理数为:'+str(sum)
                    break
                status = proxy.pop('status')
                if status == 'new':
                    if proxy not in data:
                        data.append(proxy)
                else:
                    self.update_num += 1
                    if proxy['time'] != -1: self.update_can_use_num += 1
                    db.update({'ip': proxy['ip']}, {'$set': proxy})
                if len(data) >= store_num_per:
                    db.insert_many(data)
                    self.use_num += len(data)
                    data = []
                    print u'已存储可用代理%d个.' % self.use_num
            except Empty:
                sleep(3)
            except Exception, e:
                traceback.print_exc()
                print 'error in store_use:'+str(e)

    def store_raw(self):
        db_raw = DbForRaw()
        sql = 'insert into proxy VALUES (?, ?)'
        while True:
            try:
                proxies = self.proxy_q.get_nowait()
                if proxies == 'end':
                    print "store raw proxy over, num is:" + str(self.raw_num)
                    break
                db_raw.insert_many(sql, [(proxy, raw_init_score) for proxy in proxies])
                self.raw_num += len(proxies)
                # print u'已存储代理%d个.' % self.store_num
            except Empty:
                sleep(3)
            except Exception, e:
                traceback.print_exc()
                print 'error in store_raw:'+str(e)

    def store(self):
        t_raw = Thread(target=self.store_raw)
        t_use = Thread(target=self.store_use)
        t_raw.start()
        t_use.start()
        t_raw.join()
        t_use.join()
        print u'存储代理完毕，enjoy it.'




