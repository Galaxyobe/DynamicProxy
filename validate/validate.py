# -*- coding: utf-8 -*-
import os
import sys
import time
import signal
import threading
from multiprocessing.dummy import Pool as ThreadPool
import random
import telnetlib
import logging
import subprocess
import redis
import json
import settings
import socket
import traceback
import chardet

sys.path.append("..")
from rpc.rpc import RPCServer
"""
 验证类
"""


class Validate(object):

    __running = False
    """ 初始化 """

    def __init__(self):
        # self.logger = logging.getLogger(__name__)

        self.__redis_host = settings.REDIS_HOST
        self.__redis_port = settings.REDIS_PORT

        self.__redis_items_key = settings.REDIS_ITEMS_KEY
        self.__redis_pass_items_key = settings.REDIS_PASS_ITEMS_KEY

        self.__redis_pool = redis.ConnectionPool(
            host=self.__redis_host, port=self.__redis_port)

        self.__mutex = threading.Lock()
        self.__do_threading = threading.Thread(target=self.__doing)
        self.__do_threading.setDaemon(True)
        self.__do_threading.start()
        self.__pid_path = '%s/%s' % (settings.SCRAPY_PROJECT_PATH,
                                     settings.SCRAPY_PROJECT_PID)

    """ 验证代理 """

    def __worker(self, sitem):

        try:
            item = json.loads(sitem)
            # self.__mutex.acquire()
            # print "__worker:", item
            # self.__mutex.release()

            host = item['ip'].encode("UTF-8")
            port = item['port'].encode("UTF-8")

            results = self.doValidate(host, port)

            return results, item
        except Exception, ex:
            print("#__worker %s:%s %s" % (Exception, ex))
            # traceback.print_exc()

    """ 导出通过验证的代理信息至squid的cache_peer数据格式 """

    def __export(self, item):
        # 'cache_peer 119.122.93.112 parent 8888 0 no-query weighted-round-robin weight=1 connect-fail-limit=2 allow-miss max-conn=5 name=119.122.93.112820'
        cache_peer = 'cache_peer %s parent %s 0 no-query weighted-round-robin weight=1 connect-fail-limit=2 allow-miss max-conn=5 name=%s_%s' % (
            item['ip'], item['port'], item['ip'], item['port'])

        print cache_peer

    """ 保存验证成功的代理信息 """

    def __save_passed(self, results):
        # self.__mutex.acquire()
        # print "__save_passed:", results
        # self.__mutex.release()
        try:
            r = redis.Redis(connection_pool=self.__redis_pool)
            p = r.pipeline()
            # passed = time.strftime('%Y-%m-%d %H:%M')

            for result in results:
                isOk = result[0]
                item = result[1]
                if isOk[0]:
                    p.zadd(self.__redis_pass_items_key, json.dumps(item), 0)
                else:
                    # Network is unreachable
                    if isOk[1] == 101:
                        p.sadd(self.__redis_items_key, json.dumps(item))
            p.execute()
        except Exception, ex:
            print("#__save_passed %s:%s" % (Exception, ex))

    """ 更新验证成功的代理信息 """

    def __update_passed(self, results):
        try:
            r = redis.Redis(connection_pool=self.__redis_pool)
            for result in results:
                isOk = result[0]
                item = result[1]
                # 通过验证
                if isOk[0]:
                    # 通过验证 存活 +1 正数为存活次数
                    r.zincrby(self.__redis_pass_items_key, json.dumps(item), 1)
                # 未通过验证
                else:
                    # Connection refused
                    if isOk[1] == 111:
                        live = int(
                            r.zscore(self.__redis_pass_items_key,
                                     json.dumps(item)))
                        # print item, live
                        # 存活 =-1 验证失败负数为重试次数
                        if live >= 0:
                            r.zadd(self.__redis_pass_items_key,
                                   json.dumps(item), -1)
                        # 负数为重试次数
                        else:
                            # 删除超过重试次数的代理
                            if (live * -1) >= settings.RETRY_TIMES:
                                # print 'del ', item
                                r.zrem(self.__redis_pass_items_key,
                                       json.dumps(item))
                            # 重试 -1
                            else:
                                # print '-1 ', item
                                r.zincrby(self.__redis_pass_items_key,
                                          json.dumps(item), -1)
        except Exception, ex:
            print("#__update_passed %s:%s" % (Exception, ex))

    """ start执行线程 """
    """ pid执行线程 维持可用代理的数量 """

    def __pid(self, count, level):

        try:
            r = redis.Redis(connection_pool=self.__redis_pool)
            num = int(
                r.zcount(self.__redis_pass_items_key, settings.LIVE_LEVEL,
                         '+inf'))
            # 停止抓取代理信息
            if num >= count:
                # self.logger.info("have level:%s count:%s", level, num)
                ext = os.path.exists(self.__pid_path)
                if ext:
                    try:
                        # 打开文件
                        fo = open(self.__pid_path, "r")
                        pid = fo.readline()
                        os.kill(int(pid), signal.SIGKILL)
                        os.remove(self.__pid_path)
                    except Exception, ex:
                        print("#__pid %s:%s" % (Exception, ex))
                    finally:
                        # 关闭文件
                        fo.close()
            # 开始抓取代理信息
            else:
                # 先处理已经抓取到的代理
                cnt = int(r.scard(self.__redis_items_key))
                if cnt:
                    self.start()
                else:
                    ext = os.path.exists(self.__pid_path)
                    if not ext:
                        # self.logger.info(
                        #     "start proxy crawl,now have count:%s at level:%s", num,
                        #     level)
                        subprocess.Popen(
                            'cd %s && scrapy %s' %
                            (settings.SCRAPY_PROJECT_PATH,
                             settings.SCRAPY_PROJECT_NAME),
                            shell=True,
                            stdout=open('/dev/null', 'w'),
                            stderr=subprocess.STDOUT)

        except Exception, ex:
            print("#__pid %s:%s" % (Exception, ex))
        finally:
            pass

    """ doing执行线程 循环验证代理 """

    def __doing(self):

        times = 0
        poll = settings.LIVE_PID_COUNT / settings.POOLSIZE
        if poll < 3:
            poll = 10
        count = settings.POOLSIZE
        offset = 0
        __pool = ThreadPool(settings.POOLSIZE)
        r = redis.Redis(connection_pool=self.__redis_pool)
        while True:
            times += 1
            try:
                sitems = r.zrangebylex(self.__redis_pass_items_key, '-', '+',
                                       offset, count)
                if sitems:
                    offset += count
                    results = __pool.map(self.__worker, sitems)
                    self.__update_passed(results)
                else:
                    offset = 0
                    time.sleep(5)
            except Exception, ex:
                print("#__doing %s:%s" % (Exception, ex))
            finally:
                pass
            time.sleep(0.5)
            if times % poll:
                self.__pid(settings.LIVE_PID_COUNT, settings.LIVE_LEVEL)
        __pool.close()
        __pool.join()

    """ start入口 """
    """ 取出要验证的代理信息 """
    """ 成功 - 以Redis HSET类型保存，初始分数:0 """
    """ 失败 - 丢弃 """

    def __start(self):
        try:
            self.__running = True
            __pool = ThreadPool(settings.POOLSIZE)
            while True:
                r = redis.Redis(connection_pool=self.__redis_pool)
                sitems = r.execute_command('SPOP', self.__redis_items_key,
                                           settings.POOLSIZE)
                if sitems:
                    results = __pool.map(self.__worker, sitems)
                    self.__save_passed(results)
                else:
                    break
        except Exception as ex:
            print("#__start %s:%s" % (Exception, ex))
            # traceback.print_exc()
        finally:
            __pool.close()
            __pool.join()
            self.__running = False

    """ 开启验证 """

    def start(self):
        if self.__running:
            return {'status': 'running'}
        self.__threading = threading.Thread(target=self.__start)
        self.__threading.setDaemon(True)
        self.__threading.start()
        return {'status': 'started'}

    """ 随机获取一个存活等级的代理 """

    def get(self, level, protocol=None, anonymousp=None):

        try:
            r = redis.Redis(connection_pool=self.__redis_pool)
            sitems = r.zrangebyscore(self.__redis_pass_items_key, level,
                                     '+inf', 0, settings.LIVE_PID_COUNT)
            if sitems:
                item = json.loads(random.choice(sitems))
                return item

        except Exception, ex:
            print("#get %s:%s" % (Exception, ex))
        return {}

    """ 验证代理 """

    def doValidate(self, host, port, timeout=20):
        telnet = None
        ex = 0
        try:
            telnet = telnetlib.Telnet(host, port=port, timeout=timeout)
        except socket.timeout as ex:
            # print("#doValidate %s:%s" % (socket.timeout, ex))
            return False, 110
        except socket.error as ex:
            # print("#doValidate %s:%s" % (socket.error, ex))
            (errno, err_msg) = ex
            return False, errno
        else:
            telnet.close()
            return True, None


""" 测试 """
if __name__ == "__main__":

    ip = settings.RPC_SERVER_IP
    port = settings.RPC_PORT

    RPCServer(ip, port, Validate())
