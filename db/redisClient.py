# -*- coding: utf-8 -*-
"""
-----------------------------------------------------
   File Name：     redisClient.py
   Description :   封装Redis相关操作
   Author :        JHao
   date：          2019/8/9
------------------------------------------------------
   Change Activity:
                   2019/08/09: 封装Redis相关操作
                   2020/06/23: 优化pop方法, 改用hscan命令
                   2021/05/26: 区别http/https代理
------------------------------------------------------
"""
__author__ = 'JHao'

from redis.exceptions import TimeoutError, ConnectionError, ResponseError
from redis.connection import BlockingConnectionPool
from handler.logHandler import LogHandler
from random import choice
from redis import Redis
import json


_GETDEL_SCRIPT = """
local v = redis.call('GET', KEYS[1])
redis.call('DEL', KEYS[1])
return v
"""


class RedisClient(object):
    """
    Redis client

    Redis中代理存放的结构为hash：
    key为ip:port, value为代理属性的字典;

    """

    _getdel_script = None

    def __init__(self, **kwargs):
        """
        init
        :param host: host
        :param port: port
        :param password: password
        :param db: db
        :return:
        """
        self.name = ""
        kwargs.pop("username", None)  # 使用默认值避免 KeyError
        self.__conn = Redis(connection_pool=BlockingConnectionPool(decode_responses=True,
                                                                   timeout=5,
                                                                   socket_timeout=5,
                                                                   **kwargs))

    def get(self, https):
        """
        返回一个代理
        :return:
        """
        if https:
            items = self.__conn.hvals(self.name)
            proxies = list(filter(lambda x: json.loads(x).get("https"), items))
            return choice(proxies) if proxies else None
        else:
            proxies = self.__conn.hkeys(self.name)
            proxy = choice(proxies) if proxies else None
            return self.__conn.hget(self.name, proxy) if proxy else None

    def put(self, proxy_obj):
        """
        将代理放入hash, 使用changeTable指定hash name
        :param proxy_obj: Proxy obj
        :return:
        """
        data = self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)
        return data

    def pop(self, https):
        """
        弹出一个代理
        :return: dict {proxy: value}
        """
        proxy = self.get(https)
        if proxy:
            self.__conn.hdel(self.name, json.loads(proxy).get("proxy", ""))
        return proxy if proxy else None

    def delete(self, proxy_str):
        """
        移除指定代理, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        return self.__conn.hdel(self.name, proxy_str)

    def exists(self, proxy_str):
        """
        判断指定代理是否存在, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        return self.__conn.hexists(self.name, proxy_str)

    def update(self, proxy_obj):
        """
        更新 proxy 属性
        :param proxy_obj:
        :return:
        """
        return self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)

    def getAll(self, https):
        """
        字典形式返回所有代理, 使用changeTable指定hash name
        :return:
        """
        items = self.__conn.hvals(self.name)
        if https:
            return list(filter(lambda x: json.loads(x).get("https"), items))
        else:
            return items

    def clear(self):
        """
        清空所有代理, 使用changeTable指定hash name
        :return:
        """
        return self.__conn.delete(self.name)

    def getCount(self):
        """
        返回代理数量
        :return:
        """
        proxies = self.getAll(https=False)
        return {'total': len(proxies), 'https': len(list(filter(lambda x: json.loads(x).get("https"), proxies)))}

    def changeTable(self, name):
        """
        切换操作对象
        :param name:
        :return:
        """
        self.name = name

    def setSignal(self, key, value, ex=None, nx=False):
        """设置信号键，用于跨进程通信。nx=True 时仅当键不存在才设置"""
        return self.__conn.set(key, value, ex=ex, nx=nx)

    def getSignal(self, key):
        """原子获取信号键值并删除（Lua 脚本，防止并发重复读取）"""
        try:
            if self._getdel_script is None:
                self._getdel_script = self.__conn.register_script(_GETDEL_SCRIPT)
            return self._getdel_script(keys=[key])
        except Exception:
            # Fallback: 非 Lua 环境（如旧版 SSDB）降级为 GET+DEL
            v = self.__conn.get(key)
            if v is not None:
                self.__conn.delete(key)
            return v

    def existsSignal(self, key):
        """检查信号键是否存在（不消费）"""
        return self.__conn.exists(key)

    def deleteSignal(self, key):
        """删除信号键"""
        return self.__conn.delete(key)

    def test(self):
        log = LogHandler('redis_client')
        try:
            self.getCount()
        except TimeoutError as e:
            log.error('redis connection time out: %s' % str(e), exc_info=True)
            return e
        except ConnectionError as e:
            log.error('redis connection error: %s' % str(e), exc_info=True)
            return e
        except ResponseError as e:
            log.error('redis connection error: %s' % str(e), exc_info=True)
            return e


