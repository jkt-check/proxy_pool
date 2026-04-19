# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Proxy
   Description :   代理对象类型封装
   Author :        JHao
   date：          2019/7/11
-------------------------------------------------
   Change Activity:
                   2019/7/11: 代理对象类型封装
                   2024/4/19: 添加类型提示
-------------------------------------------------
"""
__author__ = 'JHao'

import json
from typing import Optional, Dict, Any, List


class Proxy(object):

    def __init__(self, proxy: str, fail_count: int = 0, region: str = "", anonymous: str = "",
                 source: str = "", check_count: int = 0, last_status: str = "",
                 last_time: str = "", https: bool = False):
        self._proxy: str = proxy
        self._fail_count: int = fail_count
        self._region: str = region
        self._anonymous: str = anonymous
        self._source: List[str] = source.split('/')
        self._check_count: int = check_count
        self._last_status: str = last_status
        self._last_time: str = last_time
        self._https: bool = https

    @classmethod
    def createFromJson(cls, proxy_json: str) -> 'Proxy':
        _dict: Dict[str, Any] = json.loads(proxy_json)
        return cls(proxy=_dict.get("proxy", ""),
                   fail_count=_dict.get("fail_count", 0),
                   region=_dict.get("region", ""),
                   anonymous=_dict.get("anonymous", ""),
                   source=_dict.get("source", ""),
                   check_count=_dict.get("check_count", 0),
                   last_status=_dict.get("last_status", ""),
                   last_time=_dict.get("last_time", ""),
                   https=_dict.get("https", False)
                   )

    @property
    def proxy(self) -> str:
        """ 代理 ip:port """
        return self._proxy

    @property
    def fail_count(self) -> int:
        """ 检测失败次数 """
        return self._fail_count

    @property
    def region(self) -> str:
        """ 地理位置(国家/城市) """
        return self._region

    @property
    def anonymous(self) -> str:
        """ 匿名 """
        return self._anonymous

    @property
    def source(self) -> str:
        """ 代理来源 """
        return '/'.join(self._source)

    @property
    def check_count(self) -> int:
        """ 代理检测次数 """
        return self._check_count

    @property
    def last_status(self) -> str:
        """ 最后一次检测结果  True -> 可用; False -> 不可用"""
        return self._last_status

    @property
    def last_time(self) -> str:
        """ 最后一次检测时间 """
        return self._last_time

    @property
    def https(self) -> bool:
        """ 是否支持https """
        return self._https

    @property
    def to_dict(self) -> Dict[str, Any]:
        """ 属性字典 """
        return {"proxy": self.proxy,
                "https": self.https,
                "fail_count": self.fail_count,
                "region": self.region,
                "anonymous": self.anonymous,
                "source": self.source,
                "check_count": self.check_count,
                "last_status": self.last_status,
                "last_time": self.last_time}

    @property
    def to_json(self) -> str:
        """ 属性json格式 """
        return json.dumps(self.to_dict, ensure_ascii=False)

    @fail_count.setter
    def fail_count(self, value: int):
        self._fail_count = value

    @check_count.setter
    def check_count(self, value: int):
        self._check_count = value

    @last_status.setter
    def last_status(self, value):
        self._last_status = value

    @last_time.setter
    def last_time(self, value: str):
        self._last_time = value

    @https.setter
    def https(self, value: bool):
        self._https = value

    @region.setter
    def region(self, value: str):
        self._region = value

    @source.setter
    def source(self, value: str):
        self._source = value.split('/') if value else []

    def add_source(self, source_str: str):
        if source_str:
            self._source.append(source_str)
            self._source = list(set(self._source))
