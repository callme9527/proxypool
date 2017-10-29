# coding:utf-8
'''
  author : 9527
  time : 2017/10/27 8:06
'''
from flask import Flask, jsonify
from db import DbForUse

app = Flask(__name__)
db = DbForUse()


@app.route('/get/<int:type>/<int:num>')
def get(type, num):
    sql = {'type': type, 'time': {'$gt': 0}}
    proxies = db.find(sql=sql, num=num)
    res = []
    for proxy in proxies:
        proxy.pop('_id')
        res.append(proxy)
    return jsonify(tuple(res))


def run():
    app.run()
