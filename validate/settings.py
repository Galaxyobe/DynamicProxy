# -*- coding: utf-8 -*-

# Configure Redis

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

REDIS_ITEMS_KEY = 'proxy:items'
REDIS_PASS_ITEMS_KEY = 'proxy_pass:items'

# Configure RPC

RPC_SERVER_IP = '127.0.0.1'
RPC_CLIENT_IP = '127.0.0.1'
RPC_PORT = 4242

# Configure Threadpool

POOLSIZE = 30

# Configure Export

EXPORT_FILE = '/home/obe/.squid/peer.conf'

# Configure Retry

RETRY_TIMES = 8

# Configure Proxy can use live level

# 可使用代理的等级
LIVE_LEVEL = 4

# 维持等级为LIVE_LEVEL的代理数量
LIVE_PID_COUNT = 200

# Configure Scrapy

SCRAPY_PROJECT_PATH = '/home/obe/Program/workspace/scrapy/proxy'
SCRAPY_PROJECT_NAME = 'proxy'
SCRAPY_PROJECT_PID = '.proxy.pid'
