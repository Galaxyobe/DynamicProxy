# -*- coding: utf-8 -*-
# project api
from ..spiders.mmspider import MMSpider
from ..rules.rule import ProxyRules
# scrapy api
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.commands import ScrapyCommand
from scrapy.utils.conf import arglist_to_dict
import logging



class ProxyCommand(ScrapyCommand):

    requires_project = True
    default_settings = {'LOG_ENABLED': False}

    logger = logging.getLogger(__name__)

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Schedule a run for all available spiders'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option(
            "-a",
            dest="spargs",
            action="append",
            default=[],
            metavar="NAME=VALUE",
            help="set spider argument (may be repeated)")
        parser.add_option(
            "-o",
            "--output",
            metavar="FILE",
            help="dump scraped items into FILE (use - for stdout)")
        parser.add_option(
            "-t",
            "--output-format",
            metavar="FORMAT",
            help="format to use for dumping items with -o")

    def process_options(self, args, opts):
        ScrapyCommand.process_options(self, args, opts)
        try:
            opts.spargs = arglist_to_dict(opts.spargs)
        except ValueError:
            raise UsageError(
                "Invalid -a value, use -a NAME=VALUE", print_help=False)

    def run(self, args, opts):
        """ 根据项目设置实例化处理进程 """
        process = CrawlerProcess(get_project_settings())
        """ 根据规则启动爬虫 """
        proxyRules = ProxyRules()
        for (k, v) in proxyRules.Rules.iteritems():
            if isinstance(v, dict):
                if 'enable' in v and v['enable']:
                    self.logger.info("Start spider name:%s rule:%s" %
                                     (v['name'], k))
                    process.crawl(MMSpider, v)

        # the script will block here until the crawling is finished
        process.start()

