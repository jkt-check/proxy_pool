# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyHandler.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/03:
                   2020/05/26: 区分http和https
                   2024/04/19: 添加类型提示
-------------------------------------------------
"""
__author__ = 'JHao'

from typing import Optional, List, Dict
from helper.proxy import Proxy
from db.dbClient import DbClient
from handler.configHandler import ConfigHandler


class ProxyHandler(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.db = DbClient(self.conf.dbConn)
        self.db.changeTable(self.conf.tableName)

    def get(self, https: bool = False) -> Optional[Proxy]:
        """
        return a proxy
        Args:
            https: True/False
        Returns:
            Proxy object or None
        """
        proxy = self.db.get(https)
        return Proxy.createFromJson(proxy) if proxy else None

    def pop(self, https: bool = False) -> Optional[Proxy]:
        """
        return and delete a useful proxy
        :return: Proxy object or None
        """
        proxy = self.db.pop(https)
        if proxy:
            return Proxy.createFromJson(proxy)
        return None

    def put(self, proxy: Proxy):
        """
        put proxy into use proxy
        :return:
        """
        self.db.put(proxy)

    def delete(self, proxy: Proxy):
        """
        delete useful proxy
        :param proxy:
        :return:
        """
        return self.db.delete(proxy.proxy)

    def getAll(self, https: bool = False) -> List[Proxy]:
        """
        get all proxy from pool as Proxy list
        :return: List of Proxy objects
        """
        proxies = self.db.getAll(https)
        return [Proxy.createFromJson(_) for _ in proxies]

    def exists(self, proxy: Proxy) -> bool:
        """
        check proxy exists
        :param proxy:
        :return: bool
        """
        return self.db.exists(proxy.proxy)

    def getCount(self) -> Dict[str, int]:
        """
        return raw_proxy and use_proxy count
        :return: dict with count
        """
        total_use_proxy = self.db.getCount()
        return {'count': total_use_proxy}
