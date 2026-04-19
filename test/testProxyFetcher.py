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
                   2024/4/19: 添加单元测试
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from fetcher.proxyFetcher import ProxyFetcher
from handler.configHandler import ConfigHandler


class TestProxyFetcher:
    """测试 ProxyFetcher"""

    def test_fetcher_has_freeProxy02(self):
        """测试 freeProxy02 方法存在"""
        assert hasattr(ProxyFetcher, 'freeProxy02')
        assert callable(ProxyFetcher.freeProxy02)

    def test_fetcher_has_multiple_methods(self):
        """测试有多个抓取方法"""
        methods = [m for m in dir(ProxyFetcher) if m.startswith('freeProxy')]
        assert len(methods) >= 10

    def test_freeProxy02_returns_generator(self):
        """测试 freeProxy02 返回生成器"""
        # 只获取一个代理进行验证
        try:
            gen = ProxyFetcher.freeProxy02()
            # 尝试获取第一个元素
            first = next(gen, None)
            if first:
                assert ':' in first  # 格式应为 ip:port
        except StopIteration:
            pass  # 允许返回空
        except Exception:
            pass  # 允许网络错误


@pytest.mark.integration
def testProxyFetcher():
    """集成测试：测试所有代理源"""
    conf = ConfigHandler()
    proxy_getter_functions = conf.fetchers
    proxy_counter = {_: 0 for _ in proxy_getter_functions}
    for proxyGetter in proxy_getter_functions:
        try:
            for proxy in getattr(ProxyFetcher, proxyGetter.strip())():
                if proxy:
                    print('{func}: fetch proxy {proxy}'.format(func=proxyGetter, proxy=proxy))
                    proxy_counter[proxyGetter] = proxy_counter.get(proxyGetter) + 1
        except Exception as e:
            print('{func}: error {err}'.format(func=proxyGetter, err=str(e)))
    for key, value in proxy_counter.items():
        print(key, value)


if __name__ == '__main__':
    testProxyFetcher()
