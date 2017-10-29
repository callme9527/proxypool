# coding:utf-8
'''
  author : 9527
'''
import sqlite3
from pymongo import MongoClient
from gevent.lock import RLock

from conf import raw_db, db_host, db_port, db_name, db_collect


class Singleton(type):

    _instance = {}

    def __call__(self, *args, **kwargs):
        return self._instance.setdefault(self, super(Singleton, self).__call__(*args, **kwargs))


__metaclass__ = Singleton


# 存储原始的代理，没验证过
class DbForRaw:
    def __init__(self):
        self.con = sqlite3.connect(raw_db)
        self.cur = self.con.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS proxy (proxy varchar(100), left int)')

    def find(self, query, start=-1, num=-1):
        sql = 'select * from proxy where '+query+' limit '+str(start)+', '+str(num)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        return res

    def insert(self, sql, arg):
        self.cur.execute(sql, arg)
        self.con.commit()

    def update(self, set, query):
        sql = 'update proxy set '+set+' where '+query
        self.cur.execute(sql)
        self.con.commit()

    def insert_many(self, sql, args):
        self.cur.executemany(sql, args)
        self.con.commit()


# 存储能用的代理
class DbForUse:
    def __init__(self):
        self.client = MongoClient(db_host, db_port)
        self.db = self.client[db_name][db_collect]

    def insert_many(self, sql):
        self.db.insert_many(sql)

    def find(self, sql=None, skip=None, num=None):
        num = num or 0
        skip = skip or 0
        sql = sql or {}
        sort = [('score', -1), ('time', 1)]
        res = self.db.find(sql).sort(sort).skip(skip).limit(num)
        return res

    def update(self, query, new):
        self.db.update(query, new)

    def close(self):
        self.client.close()




