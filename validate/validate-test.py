# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import settings
sys.path.append("..")
from rpc.rpc import RPCClient
""" 测试 """
if __name__ == "__main__":

    ip = settings.RPC_SERVER_IP
    port = settings.RPC_PORT

    rpc = RPCClient(ip, port)
    client = rpc.getClient()

    print client.start()
    while True:
        print client.get(4)
        time.sleep(2)
