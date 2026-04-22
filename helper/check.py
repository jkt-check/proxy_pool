# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     check
   Description :   执行代理校验
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06: 执行代理校验
                   2021/05/25: 分别校验http和https
                   2022/08/16: 获取代理Region信息
                   2024/04/19: 改进异常处理，添加日志记录
-------------------------------------------------
"""
__author__ = 'JHao'

from util.six import Empty
from threading import Thread, Lock
from datetime import datetime
from util.webRequest import WebRequest
from handler.logHandler import LogHandler
from helper.validator import ProxyValidator
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


class _RateLimiter(object):
    """滑动窗口速率限制器，用于限制 ip-api.com 调用频率"""

    def __init__(self, max_calls, period_seconds):
        self._max_calls = max_calls
        self._period = period_seconds
        self._lock = Lock()
        self._timestamps = []

    def allow(self):
        """检查是否允许调用，返回 True/False"""
        with self._lock:
            now = datetime.now().timestamp()
            # 清除过期的时间戳
            cutoff = now - self._period
            self._timestamps = [t for t in self._timestamps if t > cutoff]
            if len(self._timestamps) >= self._max_calls:
                return False
            self._timestamps.append(now)
            return True


_region_limiter = _RateLimiter(40, 60)  # ip-api.com 免费限额 45次/分钟，留 5 次余量


class DoValidator(object):
    """ 执行校验 """

    conf = ConfigHandler()
    _log = LogHandler("validator")

    @classmethod
    def validator(cls, proxy, work_type):
        """
        校验入口
        Args:
            proxy: Proxy Object
            work_type: raw/use
        Returns:
            Proxy Object
        """
        http_r = cls.httpValidator(proxy)
        https_r = False if not http_r else cls.httpsValidator(proxy)

        proxy.check_count += 1
        proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proxy.last_status = True if http_r else False
        if http_r:
            if proxy.fail_count > 0:
                proxy.fail_count -= 1
            proxy.https = True if https_r else False
            if work_type == "raw":
                proxy.region = cls.regionGetter(proxy) if cls.conf.proxyRegion else ""
        else:
            proxy.fail_count += 1
        return proxy

    @classmethod
    def httpValidator(cls, proxy):
        for func in ProxyValidator.http_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def httpsValidator(cls, proxy):
        for func in ProxyValidator.https_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def preValidator(cls, proxy):
        for func in ProxyValidator.pre_validator:
            if not func(proxy):
                return False
        return True

    @classmethod
    def regionGetter(cls, proxy):
        """获取代理地理位置（通过 ip-api.com），失败时返回空字符串
        内置速率限制器（40次/分钟），超出限额时跳过查询并记录日志
        """
        if not _region_limiter.allow():
            cls._log.debug("regionGetter: rate limit exceeded, skipping %s" % proxy.proxy)
            return ""
        try:
            ip = proxy.proxy.split(':')[0]
            url = 'http://ip-api.com/json/%s?lang=zh-CN' % ip
            r = WebRequest().get(url=url, retry_time=0, timeout=3, retry_interval=0)
            if r is None:
                cls._log.warning("regionGetter: failed to get region for %s" % proxy.proxy)
                return ""
            data = r.json
            if not data or data.get('status') != 'success':
                reason = data.get('message', 'unknown') if data else 'empty response'
                cls._log.warning("regionGetter: invalid response for %s: %s" % (proxy.proxy, reason))
                return ""
            parts = [data.get('country', ''), data.get('regionName', ''), data.get('city', '')]
            address = ' '.join(p for p in parts if p)
            return address or ""
        except Exception as e:
            cls._log.error("regionGetter error for %s: %s" % (proxy.proxy, str(e)))
            return ""


class _ThreadChecker(Thread):
    """ 多线程检测 """

    def __init__(self, work_type, target_queue, thread_name):
        Thread.__init__(self, name=thread_name)
        self.work_type = work_type
        self.log = LogHandler("checker")
        self.proxy_handler = ProxyHandler()
        self.target_queue = target_queue
        self.conf = ConfigHandler()

    def run(self):
        self.log.info("{}ProxyCheck - {}: start".format(self.work_type.title(), self.name))
        while True:
            try:
                proxy = self.target_queue.get(block=False)
            except Empty:
                self.log.info("{}ProxyCheck - {}: complete".format(self.work_type.title(), self.name))
                break
            try:
                proxy = DoValidator.validator(proxy, self.work_type)
                if self.work_type == "raw":
                    self.__ifRaw(proxy)
                else:
                    self.__ifUse(proxy)
            except Exception as e:
                self.log.error("{}ProxyCheck - {}: error for {}: {}".format(
                    self.work_type.title(), self.name,
                    getattr(proxy, 'proxy', '?'), str(e)))
            self.target_queue.task_done()

    def __ifRaw(self, proxy):
        if proxy.last_status:
            if self.proxy_handler.exists(proxy):
                self.log.info('RawProxyCheck - {}: {} exist'.format(self.name, proxy.proxy.ljust(23)))
            else:
                self.log.info('RawProxyCheck - {}: {} pass'.format(self.name, proxy.proxy.ljust(23)))
                self.proxy_handler.put(proxy)
        else:
            self.log.info('RawProxyCheck - {}: {} fail'.format(self.name, proxy.proxy.ljust(23)))

    def __ifUse(self, proxy):
        if proxy.last_status:
            self.log.info('UseProxyCheck - {}: {} pass'.format(self.name, proxy.proxy.ljust(23)))
            self.proxy_handler.put(proxy)
        else:
            if proxy.fail_count > self.conf.maxFailCount:
                self.log.info('UseProxyCheck - {}: {} fail, count {} delete'.format(self.name,
                                                                                    proxy.proxy.ljust(23),
                                                                                    proxy.fail_count))
                self.proxy_handler.delete(proxy)
            else:
                self.log.info('UseProxyCheck - {}: {} fail, count {} keep'.format(self.name,
                                                                                  proxy.proxy.ljust(23),
                                                                                  proxy.fail_count))
                self.proxy_handler.put(proxy)


def Checker(tp, queue):
    """
    run Proxy ThreadChecker
    :param tp: raw/use
    :param queue: Proxy Queue
    :return:
    """
    conf = ConfigHandler()
    thread_count = conf.checkerThreadCount
    thread_list = list()
    for index in range(thread_count):
        thread_list.append(_ThreadChecker(tp, queue, "thread_%s" % str(index).zfill(2)))

    for thread in thread_list:
        thread.setDaemon(True)
        thread.start()

    for thread in thread_list:
        thread.join()
