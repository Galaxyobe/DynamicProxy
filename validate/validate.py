# -*- coding: utf-8 -*-
import os
import sys
import time
import signal
import threading
from threading import current_thread
from multiprocessing.dummy import Pool as ThreadPool
import random
import telnetlib
import logging
import sqlite3
import settings
sys.path.append("..")
from rpc.rpc import RPCServer


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Validate(object):

    __running = False

    def __init__(self):
        self.logger = logging.getLogger()
        self.__mutex = threading.Lock()
        self.__sqlite_db = settings.SQLITE_DATABASE
        self.__sqlite_table = settings.SQLITE_TABLE
        # 连接数据库 建立数据表及索引
        self.__conn = sqlite3.connect(self.__sqlite_db)
        # 指定工厂方法
        self.__conn.row_factory = dict_factory
        self.__cur = self.__conn.cursor()
        self.__create_table(self.__cur)
        self.__create_index(self.__cur)
        self.__conn.close()
        self.__do_threading = threading.Thread(target=self.__doing)
        self.__do_threading.setDaemon(True)
        self.__do_threading.start()
        self.__pid_path = '%s/%s' % (settings.SCRAPY_PROJECT_PATH,
                                     settings.SCRAPY_PROJECT_PID)

    """ 验证代理 """

    def __worker(self, item):
        # self.__mutex.acquire()
        passed = self.doValidate(item['ip'].encode("utf-8"),
                                 item['port'].encode("utf-8"))
        # self.__mutex.release()
        if passed:
            return True, item
        else:
            return False, item

    """ 导出通过验证的代理信息至squid的cache_peer数据格式 """

    def __export(self, item):
        # 'cache_peer 119.122.93.112 parent 8888 0 no-query weighted-round-robin weight=1 connect-fail-limit=2 allow-miss max-conn=5 name=119.122.93.112820'
        cache_peer = 'cache_peer %s parent %s 0 no-query weighted-round-robin weight=1 connect-fail-limit=2 allow-miss max-conn=5 name=%s_%s' % (
            item['ip'], item['port'], item['ip'], item['port'])

        print cache_peer

    """ 创建通过验证的代理信息表 """
    """ live [INT] 生存次数 """
    """ retry [INT] 重新验证次数 """

    def __create_table(self, cursor):
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS %s_pass( \
                                        id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                        ip TEXT NOT NULL, \
                                        port TEXT NOT NULL, \
                                        anonymousp TEXT NOT NULL, \
                                        protocol TEXT NOT NULL, \
                                        live INT DEFAULT 0, \
                                        retry INT DEFAULT 0, \
                                        passed TEXT \
                                        )" % self.__sqlite_table)
        except Exception, ex:
            print("#__create_table %s:%s" % (Exception, ex))

    """ 创建通过验证的代理信息表索引 """

    def __create_index(self, cursor):
        try:
            cursor.execute("CREATE INDEX %s_index ON %s_pass( \
                                        id, \
                                        ip, \
                                        port, \
                                        anonymousp, \
                                        protocol, \
                                        live,   \
                                        retry.  \
                                        passed \
                                        )" %
                           (self.__sqlite_table, self.__sqlite_table))
        except Exception, ex:
            print("#__create_index %s:%s" % (Exception, ex))

    """ 保存验证成功的代理信息 """

    def __save_passed(self, results):
        try:
            for result in results:
                if result[0]:

                    item = result[1]
                    self.__cur1.execute(
                        "SELECT ip,port,anonymousp,protocol FROM %s_pass \
                                                    WHERE ip LIKE ? \
                                                    AND port LIKE ? \
                                                    AND anonymousp LIKE ? \
                                                    AND protocol LIKE ?" %
                        self.__sqlite_table, (item['ip'], item['port'],
                                              item['anonymousp'],
                                              item['protocol']))
                    result = self.__cur1.fetchone()
                    if not result:
                        self.__mutex.acquire()
                        item["passed"] = time.strftime('%Y-%m-%d %H:%M')
                        self.__cur1.execute(
                            "INSERT INTO %s_pass (ip, port, anonymousp, protocol, passed) "
                            "VALUES (?, ?, ?, ?, ?)" % self.__sqlite_table,
                            (item['ip'], item['port'], item['anonymousp'],
                             item['protocol'], item['passed']))
                        self.__conn1.commit()
                        self.__mutex.release()
        except Exception, ex:
            print("#__save_passed %s:%s" % (Exception, ex))

    """ 更新验证成功的代理信息 """

    def __update_passed(self, results):
        try:
            for result in results:
                item = result[1]
                self.__cur2.execute(
                    "SELECT id,ip,port,anonymousp,protocol,live,retry FROM %s_pass \
                                                    WHERE ip LIKE ? \
                                                    AND port LIKE ? \
                                                    AND anonymousp LIKE ? \
                                                    AND protocol LIKE ?" %
                    self.__sqlite_table, (item['ip'], item['port'],
                                          item['anonymousp'],
                                          item['protocol']))
                ret = self.__cur2.fetchone()
                if ret:
                    self.__mutex.acquire()
                    # 通过验证
                    if result[0]:
                        ret['live'] += 1  # 通过验证 存活 +1
                        self.__cur2.execute(
                            "UPDATE %s_pass SET live = ?, retry = ? WHERE id = ?"
                            % self.__sqlite_table, (ret['live'], 0, ret['id']))
                    else:
                        ret['retry'] += 1  # 未通过验证 重试 +1
                        if ret['retry'] > settings.RETRY_TIMES:
                            self.__cur2.execute(
                                "DELETE FROM %s_pass WHERE id = %s" %
                                (self.__sqlite_table, ret['id']))
                        else:
                            self.__cur2.execute(
                                "UPDATE %s_pass SET live = ?, retry = ? WHERE id = ?"
                                % self.__sqlite_table,
                                (0, ret['retry'], ret['id']))

                    self.__conn2.commit()
                    self.__mutex.release()
        except Exception, ex:
            print("#__update_passed %s:%s" % (Exception, ex))

    """ start执行线程 """

    def __start(self):
        try:
            # 连接数据库 建立数据表及索引
            self.__conn1 = sqlite3.connect(self.__sqlite_db)
            # 指定工厂方法
            self.__conn1.row_factory = dict_factory
            self.__cur1 = self.__conn1.cursor()
            self.__create_table(self.__cur1)
            self.__create_index(self.__cur1)
            limit = settings.POOLSIZE / 2
            offset = 0
            self.__running = True
            while True:
                self.__cur1.execute("SELECT * FROM %s LIMIT %s OFFSET %s" %
                                    (self.__sqlite_table, limit, offset))
                items = self.__cur1.fetchall()
                if items:
                    offset += limit
                    for item in items:
                        self.__cur1.execute("DELETE FROM %s WHERE id = %s" %
                                            (self.__sqlite_table, item['id']))
                    __pool = ThreadPool(len(items))
                    self.__conn.commit()
                    results = __pool.map(self.__worker, items)
                    self.__save_passed(results)
                    __pool.close()
                    __pool.join()
                else:
                    self.__running = False
                    break

        except Exception, ex:
            print("%s:%s" % (Exception, ex))
        finally:
            self.__conn1.close()

    """ pid执行线程 维持可用代理的数量 """

    def __pid(self, count, level):

        try:
            self.__cur2.execute("SELECT count(*) FROM %s_pass WHERE live >= %s"
                                % (self.__sqlite_table, level))
            qty = self.__cur2.fetchone()['count(*)']

            if qty >= count:
                # 停止抓取代理信息
                try:
                    # 打开文件
                    fo = open(self.__pid_path, "r")
                    pid = fo.readline()
                    # 关闭文件
                    fo.close()
                    os.kill(int(pid), signal.SIGKILL)
                    os.remove(self.__pid_path)
                except Exception, ex:
                    print("#__pid %s:%s" % (Exception, ex))

            else:
                # 开始抓取代理信息
                ext = os.path.exists(self.__pid_path)

                if not ext:
                    time.sleep(5)
                    os.popen(
                        'cd %s && scrapy %s' % (settings.SCRAPY_PROJECT_PATH,
                                                settings.SCRAPY_PROJECT_NAME))
        except Exception, ex:
            print("#__pid %s:%s" % (Exception, ex))
        finally:
            pass

    """ doing执行线程 循环验证代理 """

    def __doing(self):

        limit = settings.POOLSIZE
        offset = 0

        while True:
            try:
                # 连接数据库 建立数据表及索引
                self.__conn2 = sqlite3.connect(self.__sqlite_db)
                # 指定工厂方法
                self.__conn2.row_factory = dict_factory
                self.__cur2 = self.__conn2.cursor()

                self.__cur2.execute("SELECT * FROM %s_pass LIMIT %s OFFSET %s"
                                    % (self.__sqlite_table, limit, offset))
                items = self.__cur2.fetchall()

                if items:
                    offset += limit
                    __pool = ThreadPool(len(items))
                    results = __pool.map(self.__worker, items)
                    self.__update_passed(results)
                    __pool.close()
                    __pool.join()
                else:
                    offset = 0
                    time.sleep(5)
                    self.__pid(settings.LIVE_PID_COUNT, settings.LIVE_LEVEL)
            except Exception, ex:
                print("#__doing %s:%s" % (Exception, ex))
            finally:
                self.__conn2.close()
            time.sleep(0.5)

    """ start入口 """

    def start(self):
        if self.__running:
            return {'status': 'running'}
        self.__threading = threading.Thread(target=self.__start)
        self.__threading.setDaemon(True)
        self.__threading.start()
        return {'status': 'started'}

    """ 随机获取一个存活等级的代理 """

    def get(self, level, protocol=None, anonymousp=None):
        if not protocol:
            protocol = '%'
        if not anonymousp:
            anonymousp = '%'
        try:
            # 连接数据库 建立数据表及索引
            self.__conn = sqlite3.connect(self.__sqlite_db)
            # 指定工厂方法
            self.__conn.row_factory = dict_factory
            self.__cur = self.__conn.cursor()
            self.__cur.execute("SELECT ip,port,live,protocol FROM %s_pass \
                                                    WHERE live >= ? \
                                                    AND protocol LIKE ? \
                                                    AND anonymousp LIKE ? \
                                                    " % self.__sqlite_table,
                               (level, protocol, anonymousp))
            items = self.__cur.fetchall()
            self.__conn.close()
            if items:
                item = random.choice(items)
                return item
        except Exception, ex:
            print("#get %s:%s" % (Exception, ex))
        return None

    """ 验证代理 """

    def doValidate(self, host, port, timeout=20):
        telnet = None
        try:
            telnet = telnetlib.Telnet(host, port=port, timeout=timeout)
        except Exception, ex:
            # print("%s:%s" % (Exception, ex))
            return False
        else:
            telnet.close()
            return True


""" 测试 """
ip = '127.0.0.1'
port = 4242

RPCServer(ip, port, Validate())
