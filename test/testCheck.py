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
                   2026/04/22: 更新测试以适配多 API 回退链
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from unittest.mock import patch, MagicMock
from helper.check import DoValidator, _RateLimiter, _LIMITERS
from helper.proxy import Proxy


def _mock_limiter_allow():
    """创建始终允许的限速器 mock"""
    mock = MagicMock()
    mock.allow.return_value = True
    return mock


def _mock_limiter_block():
    """创建始终拒绝的限速器 mock"""
    mock = MagicMock()
    mock.allow.return_value = False
    return mock


class TestDoValidator:
    """测试 DoValidator"""

    def test_regionGetter_returns_region_on_success(self):
        """主 API 成功时返回地区信息"""
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check._LIMITERS', {'ip-api.com': _mock_limiter_allow(),
                                               'ipwho.is': _mock_limiter_allow()}):
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

    def test_regionGetter_falls_back_to_secondary_on_primary_failure(self):
        """主 API 失败时回退到备用 API"""
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check._LIMITERS', {'ip-api.com': _mock_limiter_allow(),
                                               'ipwho.is': _mock_limiter_allow()}):
            with patch('helper.check.WebRequest') as mock_wr:
                # 第一次调用（ip-api.com）返回失败，第二次（ipwho.is）返回成功
                primary_resp = MagicMock()
                primary_resp.json = {"status": "fail", "message": "private range"}

                fallback_resp = MagicMock()
                fallback_resp.json = {
                    "success": True,
                    "country": "United States",
                    "region": "California",
                    "city": "Mountain View",
                }

                mock_wr.return_value.get.side_effect = [primary_resp, fallback_resp]

                result = DoValidator.regionGetter(proxy)
                assert result == "United States California Mountain View"

    def test_regionGetter_returns_empty_when_all_fail(self):
        """所有 API 均失败时返回空字符串"""
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check._LIMITERS', {'ip-api.com': _mock_limiter_allow(),
                                               'ipwho.is': _mock_limiter_allow()}):
            with patch('helper.check.WebRequest') as mock_wr:
                mock_wr.return_value.get.return_value = None

                result = DoValidator.regionGetter(proxy)
                assert result == ""

    def test_regionGetter_returns_empty_on_exception(self):
        """所有 API 均抛异常时返回空字符串"""
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check._LIMITERS', {'ip-api.com': _mock_limiter_allow(),
                                               'ipwho.is': _mock_limiter_allow()}):
            with patch('helper.check.WebRequest') as mock_wr:
                mock_wr.return_value.get.side_effect = Exception("Network error")

                result = DoValidator.regionGetter(proxy)
                assert result == ""

    def test_regionGetter_returns_empty_on_missing_data(self):
        """主 API 返回无效数据时回退到备用 API，备用也无效则返回空"""
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check._LIMITERS', {'ip-api.com': _mock_limiter_allow(),
                                               'ipwho.is': _mock_limiter_allow()}):
            with patch('helper.check.WebRequest') as mock_wr:
                primary_resp = MagicMock()
                primary_resp.json = {"status": "fail", "message": "invalid query"}

                fallback_resp = MagicMock()
                fallback_resp.json = {"success": False, "message": "Invalid IP address"}

                mock_wr.return_value.get.side_effect = [primary_resp, fallback_resp]

                result = DoValidator.regionGetter(proxy)
                assert result == ""

    def test_regionGetter_skips_rate_limited_api_and_uses_fallback(self):
        """主 API 被限流时跳过并使用备用 API"""
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check._LIMITERS', {'ip-api.com': _mock_limiter_block(),
                                               'ipwho.is': _mock_limiter_allow()}):
            with patch('helper.check.WebRequest') as mock_wr:
                fallback_resp = MagicMock()
                fallback_resp.json = {
                    "success": True,
                    "country": "Japan",
                    "region": "Tokyo",
                    "city": "Tokyo",
                }
                mock_wr.return_value.get.return_value = fallback_resp

                result = DoValidator.regionGetter(proxy)
                assert result == "Japan Tokyo Tokyo"

    def test_regionGetter_returns_empty_when_all_rate_limited(self):
        """所有 API 均被限流时返回空字符串"""
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check._LIMITERS', {'ip-api.com': _mock_limiter_block(),
                                               'ipwho.is': _mock_limiter_block()}):
            with patch('helper.check.WebRequest') as mock_wr:
                result = DoValidator.regionGetter(proxy)
                assert result == ""
                mock_wr.return_value.get.assert_not_called()

    def test_regionGetter_falls_back_when_extract_returns_empty(self):
        """主 API validate 通过但 extract 返回空字符串时回退到备用 API"""
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check._LIMITERS', {'ip-api.com': _mock_limiter_allow(),
                                               'ipwho.is': _mock_limiter_allow()}):
            with patch('helper.check.WebRequest') as mock_wr:
                # 主 API 返回有效响应但地域字段全为空
                primary_resp = MagicMock()
                primary_resp.json = {"status": "success", "country": "", "regionName": "", "city": ""}

                # 备用 API 返回有效地域
                fallback_resp = MagicMock()
                fallback_resp.json = {"success": True, "country": "Germany", "region": "Berlin", "city": "Berlin"}

                mock_wr.return_value.get.side_effect = [primary_resp, fallback_resp]

                result = DoValidator.regionGetter(proxy)
                assert result == "Germany Berlin Berlin"

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
