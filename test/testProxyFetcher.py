# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testProxyFetcher
   Description :
   Author :        JHao
   date：          2020/6/23
-------------------------------------------------
   Change Activity:
                   2020/6/23:
                   2024/4/19: 添加环境依赖跳过标记
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from fetcher.proxyFetcher import ProxyFetcher
from handler.configHandler import ConfigHandler


@pytest.mark.skip(reason="依赖外部代理网站，属于集成测试")
def testProxyFetcher():
    conf = ConfigHandler()
    proxy_getter_functions = conf.fetchers
    proxy_counter = {_: 0 for _ in proxy_getter_functions}
    for proxyGetter in proxy_getter_functions:
        for proxy in getattr(ProxyFetcher, proxyGetter.strip())():
            if proxy:
                print('{func}: fetch proxy {proxy}'.format(func=proxyGetter, proxy=proxy))
                proxy_counter[proxyGetter] = proxy_counter.get(proxyGetter) + 1
    for key, value in proxy_counter.items():
        print(key, value)


if __name__ == '__main__':
    testProxyFetcher()
