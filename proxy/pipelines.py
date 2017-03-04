# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time
import logging
import sqlite3


class ProxyPipeline(object):
    def process_item(self, item, spider):
        item["crawled"] = time.strftime('%Y-%m-%d %H:%M')
        return item


class SQLitePipeline(object):
    def __init__(self, sqlite_db, sqlite_table):
        self.sqlite_db = sqlite_db
        self.sqlite_table = sqlite_table
        self.logger = logging.getLogger(__name__)

    def drop_table(self):
        # drop table if it exists
        self.cur.execute("DROP TABLE IF EXISTS %s" % self.sqlite_table)

    def create_table(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS %s( \
                            id INTEGER PRIMARY KEY AUTOINCREMENT, \
                            ip TEXT NOT NULL, \
                            port TEXT NOT NULL, \
                            anonymousp TEXT NOT NULL, \
                            protocol TEXT NOT NULL, \
                            crawled TEXT \
                            )" % self.sqlite_table)

    def create_index(self):
        try:
            self.cur.execute("CREATE INDEX %s_index ON %s( \
                                id, \
                                ip, \
                                port, \
                                anonymousp, \
                                protocol, \
                                crawled \
                                )" % (self.sqlite_table, self.sqlite_table))
        except Exception, ex:
            self.logger.debug("%s:%s" % (Exception, ex))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(sqlite_db=crawler.settings.get('SQLITE_DATABASE'),
                   sqlite_table=crawler.settings.get('SQLITE_TABLE', 'items'))

    def open_spider(self, spider):
        self.conn = sqlite3.connect(self.sqlite_db)
        self.cur = self.conn.cursor()
        self.create_table()
        self.create_index()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        self.cur.execute("SELECT ip,port,anonymousp,protocol FROM %s \
                                WHERE ip LIKE ? \
                                AND port LIKE ? \
                                AND anonymousp LIKE ? \
                                AND protocol LIKE ?" % self.sqlite_table, (
            item['ip'], item['port'], item['anonymousp'], item['protocol']))

        result = self.cur.fetchone()
        if result:
            self.logger.debug("Item already stored in db: %s" % item)
        else:
            self.cur.execute(
                "INSERT INTO %s (ip, port, anonymousp, protocol, crawled) "
                "VALUES (?, ?, ?, ?, ?)" % self.sqlite_table,
                (item['ip'], item['port'], item['anonymousp'],
                 item['protocol'], item['crawled']))
            self.conn.commit()
            self.logger.debug("Item stored in db: %s" % item)
        return item
