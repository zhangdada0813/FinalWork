# -*- coding: utf-8 -*-
'''
Created on 2019/5/15 11:14 PM
---------
@summary:
---------
@author:
'''
import datetime
import time
from importlib import reload
from feapder.db.mysqldb import  MysqlDB
from feapder.db.redisdb import RedisDB
from handler.configHandler import ConfigHandler
from utils import tools
from handler.logHandler import LogHandler

config = ConfigHandler()
logger = LogHandler("task_manager")
class TaskManager():
    IS_IN_TIME_RANGE = 1  # 在时间范围
    NOT_REACH_TIME_RANGE = 2  # 没到达时间范围
    OVER_MIN_TIME_RANGE = 3  # 超过时间范围

    def __init__(self):
        # print()
        self._mysqldb = MysqlDB(**config.mysql_settings)
        self._redis = RedisDB(url=config.redis_conn)

        self._task_root_key = config.redis_task_root_key

        self._account_task_key = self._task_root_key + ':z_account_task'

        self._last_article_publish_time_key = self._task_root_key + ':h_last_article_publish_time'
        self._new_last_article_publish_time = self._task_root_key + ':h_new_last_article_publish_time'

        self._mysqldb.execute(config.get_create_task_Sql)
        self._mysqldb.execute(config.get_create_article_Sql)
        self._monitor_interval = config.refresh_interval
        self._zombie_account_not_publish_article_days = config.zombie_span



    def __get_task_from_redis(self, key):
        task = self._redis.zget(key, is_pop=True)
        if task:
            task = eval(task[0])
            return task

    def __random_int(self, min, max):
        pass

    def get_account_task(self):
        """
        获取公众号任务
        :return:
            {'__biz': 'Mjc1NjM3MjY2MA==', 'latest_article_publish_time': None}
            或
            None
        """
        task = self.__get_task_from_redis(self._account_task_key)
        if not task:

            logger.info("当前刷新频率为 {} 秒/次".format(str(self._monitor_interval)))
            sql = '''
                SELECT
                    user_id,
                    latest_article_publish_time
                FROM
                    douban_account_task
                WHERE
                    (
                    (
                        (
                            UNIX_TIMESTAMP(CURRENT_TIMESTAMP) - UNIX_TIMESTAMP(last_spider_time)
                        ) > {monitor_interval}
                       
                    )
                    OR (last_spider_time IS NULL)
                )
                '''.format(monitor_interval=self._monitor_interval)

            tasks = self._mysqldb.find(sql, to_json=True,limit=5)
            logger.info("获得{}个账号任务".format(str(len(tasks))))
            if tasks:
                self._redis.zadd(self._account_task_key, tasks)
                task = self.__get_task_from_redis(self._account_task_key)

        return task


    def get_last_article_publish_time(self,user_id):
        last_article_publish_time = self._redis.hget(self._last_article_publish_time_key, user_id)
        return last_article_publish_time
    def record_last_article_publish_time(self, user_id, last_publish_time):
        self._redis.hset(self._last_article_publish_time_key, user_id, last_publish_time or '')

    def is_new_update_compare_to_latest_publish_time(self, user_id, publish_time):
        latest_article_publish_time = self._redis.hget(self._last_article_publish_time, user_id)
        if not latest_article_publish_time:
            # 查询mysql里是否有该任务
            sql = "select latest_article_publish_time from douban_account_task where user_id = '%s'" % user_id
            data = self._mysqldb.find(sql)
            if data:  # [(None,)] / []
                latest_article_publish_time = str(data[0][0] or '')
                self.record_last_article_publish_time(user_id, latest_article_publish_time)

        if latest_article_publish_time is None:
            return

        if publish_time > latest_article_publish_time:
            return True

        return False

    def is_in_crawl_time_range(self, publish_time):
        """
        是否在时间范围
        :param publish_time:
        :return: 是否达时间范围
        """
        if not publish_time or (not self._crawl_time_range[0] and not self._crawl_time_range[1]):
            return TaskManager.IS_IN_TIME_RANGE

        if self._crawl_time_range[0]:  # 时间范围 上限
            if publish_time > self._crawl_time_range[0]:
                return TaskManager.NOT_REACH_TIME_RANGE

            if publish_time <= self._crawl_time_range[0] and publish_time >= self._crawl_time_range[1]:
                return TaskManager.IS_IN_TIME_RANGE

        if publish_time < self._crawl_time_range[1]:  # 下限
            return TaskManager.OVER_MIN_TIME_RANGE

        return TaskManager.IS_IN_TIME_RANGE

    def record_new_last_article_publish_time(self, user_id, new_last_publish_time):
        if not isinstance(new_last_publish_time,str):
            new_last_publish_time = datetime.datetime.strftime(new_last_publish_time,"%Y-%m-%d %H:%M:%S")
        self._redis.hset(self._new_last_article_publish_time, user_id, new_last_publish_time)

    def get_new_last_article_publish_time(self, __biz):
        return self._redis.hget(self._new_last_article_publish_time, __biz)

    def update_account_last_publish_time(self, user_id, last_publish_time):
        sql = 'update douban_account_task set latest_article_publish_time = "{}", last_spider_time="{}" where user_id="{}"'.format(
            last_publish_time, tools.get_current_date(), user_id
        )
        self._mysqldb.update(sql)

    def is_zombie_account(self, last_publish_timestamp):
        if tools.get_current_timestamp() - last_publish_timestamp > self._zombie_account_not_publish_article_days * 86400:
            return True
        return False

    def sign_account_is_zombie(self, __biz, last_publish_time=None):
        if last_publish_time:
            sql = 'update douban_account_task set last_publish_time = "{}", last_spider_time="{}", is_zombie=1 where __biz="{}"'.format(
                last_publish_time, tools.get_current_date(), __biz
            )
        else:
            sql = 'update douban_account_task set last_spider_time="{}", is_zombie=1 where __biz="{}"'.format(
                tools.get_current_date(), __biz
            )

        self._mysqldb.update(sql)

    def get_task(self, url=None, tip=''):
        """
        获取任务
        :param url: 指定url时，返回该url包装后的任务。否则先取公众号任务，无则取文章任务。若均无任务，则休眠一段时间之后再取
        :return:
        """

        # sleep_time = random.randint(self._spider_interval_min, self._spider_interval_max)

        if not url:
            account_task = self.get_account_task()
            if account_task:
                user_id = account_task.get('user_id')
                last_publish_time = account_task.get('last_publish_time')
                self.record_last_article_publish_time(user_id, last_publish_time)
                return account_task

            else:


                sleep_time = config.no_task_sleep_time
                # log.info('暂无任务 休眠 {}s'.format(sleep_time))
                logger.info('暂无任务 休眠 {}s'.format(sleep_time))
                tip = '暂无任务 '
                time.sleep(sleep_time)





    def reset_task(self):
        # 清除redis缓存
        keys = self._task_root_key + "*"
        keys = self._redis.getkeys(keys)
        if keys:
            for key in keys:
                self._redis.clear(key)




if __name__ == '__main__':
    task_manager = TaskManager()

    result = task_manager.get_task()
    print(result)
