# Dynamic Proxy

## 依赖

---

* Scrapy
* Scrapy_redis
* Redis
* Zerorpc
* python-crontab

## 介绍

---

* 使用Scrapy根据书写的规则[proxy/rules/rule.py]从网站抓取代理信息；
* 使用Xpath提取元素保存至Redis；
* 验证程序使用Python的multiprocessing开启线程池从Redis获取代理进行验证，通过验证的信息保存至Redis；
* 另外一组线程池不断的Redis获取已经通过初步验证的代理进行重复验证，对其进行评分；
* Validate程序可以对需要的代理设定一个最低可以分数，和设定一个最大可用的代理数量，如果设定分数的代理数量不足会自动开启Scrapy抓取程序，一直达到有可用的代理数量，实现动态平衡；
* 可通过linux的Crontab设置定时任务
* 使用zeroRPC模块，为应用提供获取代理的API接口


## 使用

---

### 手动开启抓取

> $ scrapy proxy

### 手动抓取后定时启动

> $ python run-proxy.py

### 启动验证和抓取

> $ python validate.py

## 示例

---

### 通过RPC获取随机一个代理信息

```python

import time
import subprocess
import settings
sys.path.append("..")
from rpc.rpc import RPCClient

if __name__ == "__main__":

    ip = settings.RPC_SERVER_IP
    port = settings.RPC_PORT

    rpc = RPCClient(ip, port)
    client = rpc.getClient()

    print client.start()
    while True:
        print client.get(4)
        time.sleep(2)
```

