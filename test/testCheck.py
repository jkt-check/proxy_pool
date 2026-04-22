# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testCheck
   Description :   check 模块单元测试
   Author :        JHao
   date：          2024/4/19
-------------------------------------------------
   Change Activity:
                   2024/4/19: TDD 测试异常处理
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from unittest.mock import patch, MagicMock
from helper.check import DoValidator, _RateLimiter, _region_limiter
from helper.proxy import Proxy


class TestDoValidator:
    """测试 DoValidator"""

    @patch('helper.check._region_limiter')
    def test_regionGetter_returns_region_on_success(self, mock_limiter):
        """成功时返回地区信息"""
        mock_limiter.allow.return_value = True
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check.WebRequest') as mock_wr:
            mock_instance = MagicMock()
            mock_instance.json = {
                "status": "success",
                "country": "中国",
                "regionName": "北京",
                "city": "北京",
            }
            mock_wr.return_value.get.return_value = mock_instance

            result = DoValidator.regionGetter(proxy)
            assert result == "中国 北京 北京"

    @patch('helper.check._region_limiter')
    def test_regionGetter_returns_empty_on_timeout(self, mock_limiter):
        """超时时应返回空字符串并记录日志"""
        mock_limiter.allow.return_value = True
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check.WebRequest') as mock_wr:
            mock_instance = MagicMock()
            mock_instance.json = None
            mock_wr.return_value.get.return_value = mock_instance

            result = DoValidator.regionGetter(proxy)
            assert result == "", f"期望空字符串，实际为 '{result}'"

    @patch('helper.check._region_limiter')
    def test_regionGetter_returns_empty_on_exception(self, mock_limiter):
        """异常时应返回空字符串并记录日志"""
        mock_limiter.allow.return_value = True
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check.WebRequest') as mock_wr:
            mock_wr.return_value.get.side_effect = Exception("Network error")

            result = DoValidator.regionGetter(proxy)
            assert result == "", f"期望空字符串，实际为 '{result}'"

    @patch('helper.check._region_limiter')
    def test_regionGetter_returns_empty_on_missing_data(self, mock_limiter):
        """数据缺失时返回空字符串"""
        mock_limiter.allow.return_value = True
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check.WebRequest') as mock_wr:
            mock_instance = MagicMock()
            mock_instance.json = {"status": "fail", "message": "invalid query"}
            mock_wr.return_value.get.return_value = mock_instance

            result = DoValidator.regionGetter(proxy)
            assert result == ""

    def test_validator_updates_proxy_check_count(self):
        """验证后代理的 check_count 应增加"""
        proxy = Proxy("127.0.0.1:8080")
        initial_count = proxy.check_count

        with patch.object(DoValidator, 'httpValidator', return_value=True):
            with patch.object(DoValidator, 'httpsValidator', return_value=False):
                result = DoValidator.validator(proxy, "raw")

        assert result.check_count == initial_count + 1

    def test_validator_sets_https_flag(self):
        """验证后应正确设置 https 标志"""
        proxy = Proxy("127.0.0.1:8080")

        with patch.object(DoValidator, 'httpValidator', return_value=True):
            with patch.object(DoValidator, 'httpsValidator', return_value=True):
                result = DoValidator.validator(proxy, "raw")

        assert result.https is True

    def test_validator_increments_fail_count_on_failure(self):
        """验证失败时 fail_count 应增加"""
        proxy = Proxy("127.0.0.1:8080")

        with patch.object(DoValidator, 'httpValidator', return_value=False):
            result = DoValidator.validator(proxy, "use")

        assert result.fail_count == 1


class TestRateLimiter:
    """测试 _RateLimiter"""

    def test_allows_calls_within_limit(self):
        """限额内应允许调用"""
        limiter = _RateLimiter(3, 60)
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is True

    def test_blocks_calls_exceeding_limit(self):
        """超出限额应拒绝调用"""
        limiter = _RateLimiter(2, 60)
        limiter.allow()
        limiter.allow()
        assert limiter.allow() is False

    def test_regionGetter_returns_empty_when_rate_limited(self):
        """限流时 regionGetter 应返回空字符串并跳过 HTTP 请求"""
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check._region_limiter') as mock_limiter:
            mock_limiter.allow.return_value = False
            with patch('helper.check.WebRequest') as mock_wr:
                result = DoValidator.regionGetter(proxy)
                assert result == ""
                mock_wr.return_value.get.assert_not_called()
