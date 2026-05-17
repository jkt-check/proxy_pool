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
                   2026/04/22: 多 API 回退链（ip-api.com → ipwho.is），提升国内可用性
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
    """滑动窗口速率限制器"""

    def __init__(self, max_calls, period_seconds):
        self._max_calls = max_calls
        self._period = period_seconds
        self._lock = Lock()
        self._timestamps = []

    def allow(self):
        """检查是否允许调用，返回 True/False"""
        with self._lock:
            now = datetime.now().timestamp()
            cutoff = now - self._period
            self._timestamps = [t for t in self._timestamps if t > cutoff]
            if len(self._timestamps) >= self._max_calls:
                return False
            self._timestamps.append(now)
            return True


# 各 API 独立速率限制器
_ipapi_limiter = _RateLimiter(40, 60)    # ip-api.com 免费限额 45次/分钟，留 5 次余量
_ipwho_limiter = _RateLimiter(20, 60)    # ipwho.is 保守限额 20次/分钟

# 限速器全局查找表，供 _REGION_APIS 引用
_LIMITERS = {
    'ip-api.com': _ipapi_limiter,
    'ipwho.is': _ipwho_limiter,
}

# Region API 回退链：依次尝试，首个成功即返回
_REGION_APIS = [
    {
        'name': 'ip-api.com',
        'url': 'http://ip-api.com/json/{ip}?lang=zh-CN&fields=status,message,country,regionName,city',
        'limiter_key': 'ip-api.com',
        'timeout': 3,
        'validate': lambda d: d.get('status') == 'success',
        'extract': lambda d: ' '.join(filter(None, [d.get('country'), d.get('regionName'), d.get('city')])),
    },
    {
        'name': 'ipwho.is',
        'url': 'https://ipwho.is/{ip}',
        'limiter_key': 'ipwho.is',
        'timeout': 5,
        'validate': lambda d: d.get('success') is True,
        'extract': lambda d: ' '.join(filter(None, [d.get('country'), d.get('region'), d.get('city')])),
    },
]


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
        """获取代理地理位置，按 _REGION_APIS 回退链依次尝试
        所有 API 均失败或被限流时返回空字符串
        """
        ip = proxy.proxy.split(':')[0]
        for api in _REGION_APIS:
            limiter = _LIMITERS.get(api['limiter_key'])
            if limiter is None:
                cls._log.warning("regionGetter: no limiter for %s, skipping"
                                 % api['name'])
                continue
            if not limiter.allow():
                cls._log.debug("regionGetter: %s rate limit exceeded, skipping %s"
                               % (api['name'], proxy.proxy))
                continue
            try:
                url = api['url'].format(ip=ip)
                r = WebRequest().get(url=url, retry_time=0, timeout=api['timeout'], retry_interval=0)
                if r is None:
                    cls._log.warning("regionGetter: %s request failed for %s"
                                     % (api['name'], proxy.proxy))
                    continue
                data = r.json
                if not data or not api['validate'](data):
                    reason = data.get('message', 'unknown') if isinstance(data, dict) else 'empty response'
                    cls._log.warning("regionGetter: %s invalid response for %s: %s"
                                     % (api['name'], proxy.proxy, reason))
                    continue
                address = api['extract'](data).strip()
                if address:
                    return address
            except Exception as e:
                cls._log.error("regionGetter: %s error for %s: %s"
                               % (api['name'], proxy.proxy, str(e)))
                continue
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
