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
from helper.check import DoValidator
from helper.proxy import Proxy


class TestDoValidator:
    """测试 DoValidator"""

    def test_regionGetter_returns_region_on_success(self):
        """成功时返回地区信息"""
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check.WebRequest') as mock_wr:
            mock_instance = MagicMock()
            mock_instance.json = {"data": {"address": "北京市"}}
            mock_wr.return_value.get.return_value = mock_instance

            result = DoValidator.regionGetter(proxy)
            assert result == "北京市"

    def test_regionGetter_returns_empty_on_timeout(self):
        """
        RED: 超时时应返回空字符串并记录日志
        """
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check.WebRequest') as mock_wr:
            mock_instance = MagicMock()
            mock_instance.json = None  # 模拟超时或失败
            mock_wr.return_value.get.return_value = mock_instance

            result = DoValidator.regionGetter(proxy)
            # 应返回空字符串而非 'error'
            assert result == "", f"期望空字符串，实际为 '{result}'"

    def test_regionGetter_returns_empty_on_exception(self):
        """
        RED: 异常时应返回空字符串并记录日志
        """
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check.WebRequest') as mock_wr:
            mock_wr.return_value.get.side_effect = Exception("Network error")

            result = DoValidator.regionGetter(proxy)
            # 应返回空字符串而非 'error'
            assert result == "", f"期望空字符串，实际为 '{result}'"

    def test_regionGetter_returns_empty_on_missing_data(self):
        """数据缺失时返回空字符串"""
        proxy = Proxy("1.2.3.4:8080")

        with patch('helper.check.WebRequest') as mock_wr:
            mock_instance = MagicMock()
            mock_instance.json = {}  # 缺少 data 字段
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
