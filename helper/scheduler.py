# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
                   2024/04/19: 使用配置替代硬编码的魔术数字
                   2026/04/22: 支持通过 Redis 信号触发刷新
-------------------------------------------------
"""
__author__ = 'JHao'

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


def __runProxyFetch():
    proxy_queue = Queue()
    proxy_fetcher = Fetcher()

    for proxy in proxy_fetcher.run():
        proxy_queue.put(proxy)

    Checker("raw", proxy_queue)


def __checkRefreshSignal():
    """检查是否收到来自 API /refresh/ 的刷新信号（原子读取并删除）"""
    conf = ConfigHandler()
    proxy_handler = ProxyHandler()
    try:
        signal = proxy_handler.db.getSignal(conf.refreshSignalKey)
        if signal:
            return True
    except Exception as e:
        scheduler_log = LogHandler("scheduler")
        scheduler_log.warning("Failed to check refresh signal: %s", str(e))
    return False


def __runProxyCheck():
    proxy_handler = ProxyHandler()
    proxy_queue = Queue()
    scheduler_log = LogHandler("scheduler")
    try:
        total = proxy_handler.db.getCount().get("total", 0)
    except Exception as e:
        scheduler_log.error("Failed to get proxy count: %s", str(e))
        total = 0
    need_fetch = total < proxy_handler.conf.poolSizeMin
    if __checkRefreshSignal():
        scheduler_log.info("Received refresh signal from API, triggering proxy fetch")
        need_fetch = True
    if need_fetch:
        __runProxyFetch()
    for proxy in proxy_handler.getAll():
        proxy_queue.put(proxy)
    Checker("use", proxy_queue)


def runScheduler():
    __runProxyFetch()

    conf = ConfigHandler()
    timezone = conf.timezone
    scheduler_log = LogHandler("scheduler")
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)

    # 使用配置的间隔时间
    scheduler.add_job(__runProxyFetch, 'interval', minutes=conf.fetchInterval, id="proxy_fetch", name="proxy采集")
    scheduler.add_job(__runProxyCheck, 'interval', minutes=conf.checkInterval, id="proxy_check", name="proxy检查")
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }

    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)

    scheduler.start()


if __name__ == '__main__':
    runScheduler()
