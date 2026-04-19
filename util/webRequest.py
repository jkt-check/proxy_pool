# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     WebRequest
   Description :   Network Requests Class
   Author :        J_hao
   date：          2017/7/31
-------------------------------------------------
   Change Activity:
                   2017/7/31:
                   2024/4/19: 重试失败返回None而非伪造响应
-------------------------------------------------
"""
__author__ = 'J_hao'

from typing import Optional
from requests.models import Response
from lxml import etree
import requests
import random
import time

from handler.logHandler import LogHandler

requests.packages.urllib3.disable_warnings()


class WebRequest(object):
    name = "web_request"

    def __init__(self, *args, **kwargs):
        self.log = LogHandler(self.name, file=False)
        self.response: Optional[Response] = None
        self._request_failed: bool = False

    @property
    def user_agent(self) -> str:
        """
        return an User-Agent at random
        :return: User-Agent string
        """
        ua_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        ]
        return random.choice(ua_list)

    @property
    def header(self) -> dict:
        """
        basic header
        :return: headers dict
        """
        return {'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Accept-Language': 'zh-CN,zh;q=0.8'}

    def get(self, url: str, header: Optional[dict] = None, retry_time: int = 3,
            retry_interval: int = 5, timeout: int = 5, *args, **kwargs) -> Optional['WebRequest']:
        """
        get method
        :param url: target url
        :param header: headers
        :param retry_time: retry time
        :param retry_interval: retry interval
        :param timeout: network timeout
        :return: WebRequest instance on success, None on failure
        """
        headers = self.header
        if header and isinstance(header, dict):
            headers.update(header)
        while True:
            try:
                self.response = requests.get(url, headers=headers, timeout=timeout, *args, **kwargs)
                self._request_failed = False
                return self
            except Exception as e:
                self.log.error("requests: %s error: %s" % (url, str(e)))
                retry_time -= 1
                if retry_time <= 0:
                    self._request_failed = True
                    self.log.error("requests: %s failed after all retries" % url)
                    return None
                self.log.info("retry %s second after" % retry_interval)
                time.sleep(retry_interval)

    @property
    def tree(self) -> Optional[etree._Element]:
        """返回 lxml 解析的 HTML 树，失败时返回 None"""
        if self._request_failed or self.response is None or not self.response.content:
            return None
        return etree.HTML(self.response.content)

    @property
    def text(self) -> str:
        """返回响应文本，失败时返回空字符串"""
        if self._request_failed or self.response is None:
            return ""
        return self.response.text

    @property
    def json(self) -> dict:
        """返回 JSON 解析结果，失败时返回空字典"""
        if self._request_failed or self.response is None:
            return {}
        try:
            return self.response.json()
        except Exception as e:
            self.log.error(str(e))
            return {}

