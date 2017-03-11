# -*- coding: utf-8 -*-
import logging
from scrapy import signals
from scrapy.exceptions import NotConfigured
import os
import sys
from scrapy.utils.project import get_project_settings
sys.path.append("..")
from rpc.rpc import RPCClient


class Extensions(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = get_project_settings()
        self.file = '.%s.pid' % self.settings['BOT_NAME']
        self.rpc = None
        self.item_count = 0

    @classmethod
    def from_crawler(cls, crawler):

        # instantiate the extension object
        ext = cls()

        # connect the extension object to signals
        crawler.signals.connect(
            ext.engine_started, signal=signals.engine_started)
        crawler.signals.connect(
            ext.engine_stopped, signal=signals.engine_stopped)
        # connect the extension object to signals
        crawler.signals.connect(
            ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(
            ext.spider_closed, signal=signals.spider_closed)

        # connect the extension object to signals
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.item_dropped, signal=signals.item_dropped)

        # return the extension object
        return ext

    def engine_started(self):
        pid = str(os.getpid())
        f = open(self.file, 'w')
        f.write(pid)
        f.close()

    def engine_stopped(self):
        os.remove(self.file)

    def spider_opened(self, spider):

        self.rpc = RPCClient(self.settings['RPC_SERVER_IP'],
                             self.settings['RPC_PORT'])
        self.client = self.rpc.getClient()
        # self.logger.info("opened spider %s", spider.name)

    def spider_closed(self, spider):
        self.rpc.close()

    def item_scraped(self, item, response, spider):
        # self.logger.info("item scraped %s", spider.name)
        self.item_count += 1
        if self.item_count >= 30:
            self.item_count = 0
            try:
                print self.client.start()
            except Exception, ex:
                print("@Extensions #item_scraped %s:%s" % (Exception, ex))

    def item_dropped(self, item, exception, spider):
        # self.logger.info("item dropped %s", spider.name)
        pass
