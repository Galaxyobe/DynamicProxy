# -*- coding: utf-8 -*-

# Configure SQLite

SQLITE_DATABASE = '../db/proxyip.db'
SQLITE_TABLE = 'source'

# Configure RPC

SERVER_IP = '127.0.0.1'
CLIENT_IP = '127.0.0.1'
PORT = 4242

# Configure Threadpool

POOLSIZE = 30

# Configure Export

EXPORT_FILE = '/home/obe/.squid/peer.conf'

# Configure Retry

RETRY_TIMES = 8

# Configure Proxy can use live level

LIVE_LEVEL = 4

# 维持等级为LIVE_LEVEL的代理数量
LIVE_PID_COUNT = 100

# Configure Scrapy

SCRAPY_PROJECT_PATH = '/home/obe/Program/workspace/scrapy/proxy'
SCRAPY_PROJECT_NAME = 'proxy'
SCRAPY_PROJECT_PID = '.proxy.pid'
