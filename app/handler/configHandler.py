# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     configHandler
   Description :
   Author :        JHao
   date：          2020/6/22
-------------------------------------------------
   Change Activity:
                   2020/6/22:
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import setting
from util.singleton import Singleton
from util.lazyProperty import LazyProperty
from util.six import reload_six, withMetaclass


class ConfigHandler(withMetaclass(Singleton)):

    def __init__(self):
        pass




    @property
    def pc_account_list(self):
        return os.getenv("PC_PASSWORD", setting.ACCOUNT_LIST)


    @property
    def phone_account_list(self):
        reload_six(setting)
        return os.getenv("PHONE_ACCOUNT", setting.PHONE_ACCOUNT_LIST)


    @LazyProperty
    def mysql_settings(self):
        return os.getenv("MYSQL_CONN", setting.MYSQL_CONN)

    # @LazyProperty
    # def proxyCheckCount(self):
    #     return int(os.getenv("PROXY_CHECK_COUNT", setting.PROXY_CHECK_COUNT))


    @property
    def mail_server(self):
        reload_six(setting)
        return os.getenv("MAIL_SERVER", setting.MAIL_SERVER)

    @property
    def mail_sender(self):
        reload_six(setting)
        return os.getenv("MAIL_SERVER", setting.MAIL_SENDER)

    @property
    def mail_passwd(self):
        reload_six(setting)
        return os.getenv("MAIL_SERVER", setting.MAIL_PASSWORD)

    @property
    def mail_receiver(self):
        reload_six(setting)
        return os.getenv("MAIL_SERVER", setting.MAIL_RECEIVER)



    # @LazyProperty
    # def maxFailRate(self):
    #     return int(os.getenv("MAX_FAIL_RATE", setting.MAX_FAIL_RATE))

    @LazyProperty
    def poolSizeMin(self):
        return int(os.getenv("POOL_SIZE_MIN", setting.POOL_SIZE_MIN))

    @LazyProperty
    def get_create_task_Sql(self):
        return os.getenv("DOUBAN_ACCOUNT_TASK_SQL", setting.DOUBAN_ACCOUNT_TASK_SQL)

    @LazyProperty
    def get_create_article_Sql(self):
        return os.getenv("DOUBAN_ARTICLE_TASK_SQL", setting.DOUBAN_ARTICLE_TASK_SQL)
    @LazyProperty
    def timezone(self):
        return os.getenv("TIMEZONE", setting.TIMEZONE)

