# -*- coding: utf-8 -*-
import logging
from scrapy import signals
from scrapy.exceptions import NotConfigured
import os
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)


class EngineStartedAndStopped(object):
    def __init__(self):
        self.settings = get_project_settings()
        self.file = '.%s.pid' % self.settings['BOT_NAME']

    @classmethod
    def from_crawler(cls, crawler):

        # instantiate the extension object
        ext = cls()

        # connect the extension object to signals
        crawler.signals.connect(
            ext.engine_started, signal=signals.engine_started)
        crawler.signals.connect(
            ext.engine_stopped, signal=signals.engine_stopped)

        # return the extension object
        return ext

    def engine_started(self):
        pid = str(os.getpid())
        f = open(self.file, 'w')
        f.write(pid)
        f.close()

    def engine_stopped(self):
        os.remove(self.file)


class SpiderOpenAndClose(object):
    def __init__(self):
        self.settings = get_project_settings()

    @classmethod
    def from_crawler(cls, crawler):

        # instantiate the extension object
        ext = cls()

        # connect the extension object to signals
        crawler.signals.connect(
            ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(
            ext.spider_closed, signal=signals.spider_closed)

        # return the extension object
        return ext

    def spider_opened(self, spider):
        logger.info("opened spider %s", spider.name)

    def spider_closed(self, spider):
        logger.info("closed spider %s", spider.name)
