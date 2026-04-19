# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testProxyHandler
   Description :   ProxyHandler 单元测试
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
from handler.proxyHandler import ProxyHandler


class TestProxyHandler:
    """测试 ProxyHandler"""

    @pytest.fixture
    def handler(self):
        """创建 ProxyHandler"""
        with patch('handler.proxyHandler.DbClient') as MockDbClient:
            mock_client = MagicMock()
            MockDbClient.return_value = mock_client
            handler = ProxyHandler()
            handler.db = mock_client
            yield handler

    def test_get_returns_proxy(self, handler):
        """测试获取代理"""
        mock_json = '{"proxy": "127.0.0.1:8080", "https": false}'
        handler.db.get.return_value = mock_json

        result = handler.get(https=False)
        assert result is not None
        assert result.proxy == "127.0.0.1:8080"

    def test_get_returns_none_when_empty(self, handler):
        """测试无代理时返回 None"""
        handler.db.get.return_value = None

        result = handler.get(https=False)
        assert result is None

    def test_pop_returns_and_deletes(self, handler):
        """测试弹出代理"""
        mock_json = '{"proxy": "127.0.0.1:8080", "https": false}'
        handler.db.pop.return_value = mock_json

        result = handler.pop(https=False)
        assert result is not None
        handler.db.pop.assert_called_once()

    def test_pop_returns_none_when_empty(self, handler):
        """测试无代理弹出时返回 None"""
        handler.db.pop.return_value = None

        result = handler.pop(https=False)
        assert result is None

    def test_put_calls_db_put(self, handler):
        """测试存入代理"""
        proxy = Proxy("127.0.0.1:8080")

        handler.put(proxy)
        handler.db.put.assert_called_once_with(proxy)

    def test_delete_calls_db_delete(self, handler):
        """测试删除代理"""
        proxy = Proxy("127.0.0.1:8080")

        handler.delete(proxy)
        handler.db.delete.assert_called_once_with("127.0.0.1:8080")

    def test_get_all_returns_list(self, handler):
        """测试获取所有代理"""
        mock_json1 = '{"proxy": "127.0.0.1:8080", "https": false}'
        mock_json2 = '{"proxy": "127.0.0.1:8081", "https": true}'
        handler.db.getAll.return_value = [mock_json1, mock_json2]

        result = handler.getAll(https=False)
        assert len(result) == 2
        assert all(isinstance(p, Proxy) for p in result)

    def test_exists_returns_true(self, handler):
        """测试代理存在"""
        proxy = Proxy("127.0.0.1:8080")
        handler.db.exists.return_value = True

        result = handler.exists(proxy)
        assert result is True
        handler.db.exists.assert_called_once_with("127.0.0.1:8080")

    def test_get_count_returns_dict(self, handler):
        """测试获取代理数量"""
        handler.db.getCount.return_value = {'total': 10, 'https': 5}

        result = handler.getCount()
        assert 'count' in result
