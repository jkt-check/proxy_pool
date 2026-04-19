# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testFetch
   Description :   Fetch 模块单元测试
   Author :        JHao
   date：          2024/4/19
-------------------------------------------------
   Change Activity:
                   2024/4/19: TDD 测试
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from unittest.mock import patch, MagicMock
from helper.proxy import Proxy


class TestFetcher:
    """测试 Fetcher"""

    def test_fetcher_init(self):
        """测试 Fetcher 初始化"""
        from helper.fetch import Fetcher
        fetcher = Fetcher()
        assert fetcher.name == "fetcher"

    def test_run_yields_proxies(self):
        """测试 run 方法返回代理生成器"""
        from helper.fetch import Fetcher

        with patch('helper.fetch.ProxyFetcher') as mock_fetcher_class:
            # 模拟 fetcher 方法
            mock_fetcher_class.freeProxy01 = MagicMock(return_value=iter(["1.1.1.1:8080", "2.2.2.2:8080"]))
            mock_fetcher_class.freeProxy02 = MagicMock(return_value=iter(["3.3.3.3:8080"]))

            with patch('helper.fetch.ConfigHandler') as mock_conf:
                mock_conf.return_value.fetchers = ["freeProxy01", "freeProxy02"]
                mock_conf.return_value.maxFailCount = 0

                fetcher = Fetcher()
                proxies = list(fetcher.run())

                # 至少会过滤格式正确的代理
                assert all(isinstance(p, Proxy) for p in proxies)
