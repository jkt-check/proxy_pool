# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testWebRequest
   Description :   WebRequest 单元测试
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
from util.webRequest import WebRequest


class TestWebRequestRetryBehavior:
    """测试 WebRequest 重试行为"""

    def test_get_returns_none_when_all_retries_fail(self):
        """
        RED: 当所有重试都失败时，应返回 None 而非伪造的 200 响应
        """
        with patch('util.webRequest.requests.get') as mock_get:
            mock_get.side_effect = ConnectionError("Connection refused")

            wr = WebRequest()
            result = wr.get("http://nonexistent.invalid", retry_time=2, retry_interval=0.1)

            # 期望: 重试失败后返回 None，而非伪造响应
            assert result is None, "重试失败后应返回 None"

    def test_get_returns_self_on_success(self):
        """
        成功请求应返回 self 以便链式调用
        """
        with patch('util.webRequest.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"<html><body>test</body></html>"
            mock_get.return_value = mock_response

            wr = WebRequest()
            result = wr.get("http://example.com")

            assert result is not None
            assert result is wr

    def test_tree_returns_none_on_failed_request(self):
        """
        RED: 当请求失败时，访问 tree 属性应返回 None
        """
        with patch('util.webRequest.requests.get') as mock_get:
            mock_get.side_effect = ConnectionError("Connection refused")

            wr = WebRequest()
            result = wr.get("http://nonexistent.invalid", retry_time=1, retry_interval=0.1)

            # 期望: 失败请求的 tree 应为 None
            assert result is None or wr.tree is None, "失败请求的 tree 应为 None"

    def test_json_returns_empty_on_failure(self):
        """
        当请求失败时，json 属性应返回空字典
        """
        with patch('util.webRequest.requests.get') as mock_get:
            mock_get.side_effect = ConnectionError("Connection refused")

            wr = WebRequest()
            result = wr.get("http://nonexistent.invalid", retry_time=1, retry_interval=0.1)

            # 失败请求的 json 应为空字典
            if result is None:
                assert wr.json == {}
            else:
                assert result.json == {}


class TestWebRequestProperties:
    """测试 WebRequest 属性"""

    def test_user_agent_returns_valid_string(self):
        """User-Agent 应返回有效字符串"""
        wr = WebRequest()
        ua = wr.user_agent
        assert isinstance(ua, str)
        assert len(ua) > 0
        assert "Mozilla" in ua

    def test_header_contains_required_fields(self):
        """Header 应包含必要字段"""
        wr = WebRequest()
        header = wr.header
        assert "User-Agent" in header
        assert "Accept" in header
        assert "Connection" in header
