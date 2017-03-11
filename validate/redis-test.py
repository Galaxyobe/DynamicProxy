# -*- coding: utf-8 -*-

import redis
import settings
import json

__redis_host = settings.REDIS_HOST
__redis_port = settings.REDIS_PORT

__redis_items_key = settings.REDIS_ITEMS_KEY
__redis_pass_items_key = settings.REDIS_PASS_ITEMS_KEY

__redis_pool = redis.ConnectionPool(host=__redis_host, port=__redis_port)

r = redis.Redis(connection_pool=__redis_pool)

t = [
    '{"ip": "106.46.136.117", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "106.46.136.79", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "117.82.39.152", "protocol": "HTTP", "port": "8998", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "60.185.142.119", "protocol": "HTTP", "port": "3128", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "183.32.88.211", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "106.46.136.169", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "106.46.136.250", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "113.69.63.237", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "113.69.253.157", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "106.46.136.42", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "183.32.88.83", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "106.46.136.195", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "119.5.0.76", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "183.32.88.104", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "111.72.126.114", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "58.33.145.255", "protocol": "HTTP", "port": "8118", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "106.46.136.111", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "110.73.32.208", "protocol": "HTTP", "port": "8123", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "110.73.2.235", "protocol": "HTTP", "port": "8123", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "119.5.1.58", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "111.72.127.107", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "119.5.1.3", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "113.69.165.90", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "106.46.136.227", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "106.46.136.210", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "183.32.88.103", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "183.32.88.26", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "122.228.179.178", "protocol": "HTTP", "port": "80", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "106.46.136.133", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
    '{"ip": "106.46.136.234", "protocol": "HTTP", "port": "808", "anonymousp": "\\u9ad8\\u533f"}',
]

# items = r.execute_command("SPOP", settings.REDIS_ITEMS_KEY, 2)
# print items

for item in t:
    r.sadd(settings.REDIS_ITEMS_KEY, item)
