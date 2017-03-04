# -*- coding: utf-8 -*-
from proxy.spiders.mmspider import MMSpider
from proxy.rules.rule import ProxyRules
# scrapy api
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging
# system api
import sys
# lib api
from crontab import CronTab

logger = logging.getLogger('run-proxy')
""" 根据项目设置实例化处理进程 """
settings = get_project_settings()
process = CrawlerProcess(settings)
""" 根据规则启动爬虫 """
proxyRules = ProxyRules()
for (k, v) in proxyRules.Rules.iteritems():
    if isinstance(v, dict):
        if 'enable' in v and v['enable']:
            logger.info("Start spider name:%s rule:%s" % (v['name'], k))
            process.crawl(MMSpider, v)

# the script will block here until the crawling is finished
process.start()

path = sys.path[0]
# 任务注释 作为标识符
comment = settings['CRONTAB_COMMENT']
# 创建当前用户的crontab，当然也可以创建其他用户的，但得有足够权限
cron = CronTab(user=True)
# 判断是否有一样的任务
for job in cron:
    if comment == job.comment:
        cron.remove_all(comment=comment)
# 创建任务
job = cron.new(command='cd %s && python %s' % (path, __file__), comment=comment)
# 设置任务执行周期，每两分钟执行一次
job.setall(settings['CRONTAB_TIME'])
cron.write()
logger.info('Set crontab:%s' % job)
