## 爬虫代理池
抓取各大代理网站的免费代理，从中验证获取高匿代理.

## 所需库
- requests
- gevent
- flask
- pymongo

## 使用
python begin.py</br>
运行一段时间，访问http://localhost:5000/[代理类型0:http,1:https,2:两者]/[需要的代理数]<br/>
如http://localhost:5000/2/5代表获取可以代理http和https的高匿代理5枚.

## 效果
![](https://github.com/callme9527/proxypool/raw/master/pic/run.png)
![](https://github.com/callme9527/proxypool/raw/master/pic/run2.png)
![](https://github.com/callme9527/proxypool/raw/master/pic/res.png)
![](https://github.com/callme9527/proxypool/raw/master/pic/api.png)
