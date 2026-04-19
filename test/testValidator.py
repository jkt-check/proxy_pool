# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testValidator
   Description :   Validator 模块单元测试
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
from helper.validator import ProxyValidator, formatValidator, httpTimeOutValidator, httpsTimeOutValidator


class TestProxyValidator:
    """测试 ProxyValidator"""

    def test_pre_validator_list_exists(self):
        """测试预验证器列表存在"""
        assert hasattr(ProxyValidator, 'pre_validator')
        assert isinstance(ProxyValidator.pre_validator, list)

    def test_http_validator_list_exists(self):
        """测试 HTTP 验证器列表存在"""
        assert hasattr(ProxyValidator, 'http_validator')
        assert isinstance(ProxyValidator.http_validator, list)

    def test_https_validator_list_exists(self):
        """测试 HTTPS 验证器列表存在"""
        assert hasattr(ProxyValidator, 'https_validator')
        assert isinstance(ProxyValidator.https_validator, list)

    def test_add_pre_validator(self):
        """测试添加预验证器"""
        initial_count = len(ProxyValidator.pre_validator)

        @ProxyValidator.addPreValidator
        def test_validator(proxy):
            return True

        assert len(ProxyValidator.pre_validator) == initial_count + 1

    def test_add_http_validator(self):
        """测试添加 HTTP 验证器"""
        initial_count = len(ProxyValidator.http_validator)

        @ProxyValidator.addHttpValidator
        def test_http_validator(proxy):
            return True

        assert len(ProxyValidator.http_validator) == initial_count + 1

    def test_add_https_validator(self):
        """测试添加 HTTPS 验证器"""
        initial_count = len(ProxyValidator.https_validator)

        @ProxyValidator.addHttpsValidator
        def test_https_validator(proxy):
            return True

        assert len(ProxyValidator.https_validator) == initial_count + 1


class TestFormatValidator:
    """测试格式验证器"""

    def test_valid_format(self):
        """测试有效格式"""
        assert formatValidator("192.168.1.1:8080") is True
        assert formatValidator("127.0.0.1:80") is True
        assert formatValidator("10.0.0.1:443") is True

    def test_valid_format_with_auth(self):
        """测试带认证的格式"""
        assert formatValidator("user:pass@192.168.1.1:8080") is True

    def test_invalid_format(self):
        """测试无效格式"""
        assert formatValidator("192.168.1.1") is False  # 缺少端口
        assert formatValidator("") is False  # 空字符串
        # 注意：正则只检查格式，不验证 IP 范围


class TestHttpValidator:
    """测试 HTTP 验证器"""

    def test_http_validator_success(self):
        """测试 HTTP 验证成功"""
        with patch('helper.validator.head') as mock_head:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_head.return_value = mock_response

            result = httpTimeOutValidator("192.168.1.1:8080")
            assert result is True

    def test_http_validator_failure(self):
        """测试 HTTP 验证失败"""
        with patch('helper.validator.head') as mock_head:
            mock_head.side_effect = Exception("Connection refused")

            result = httpTimeOutValidator("192.168.1.1:8080")
            assert result is False

    def test_http_validator_timeout(self):
        """测试 HTTP 超时"""
        with patch('helper.validator.head') as mock_head:
            mock_head.side_effect = TimeoutError("Connection timed out")

            result = httpTimeOutValidator("192.168.1.1:8080")
            assert result is False


class TestHttpsValidator:
    """测试 HTTPS 验证器"""

    def test_https_validator_success(self):
        """测试 HTTPS 验证成功"""
        with patch('helper.validator.head') as mock_head:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_head.return_value = mock_response

            result = httpsTimeOutValidator("192.168.1.1:8080")
            assert result is True

    def test_https_validator_failure(self):
        """测试 HTTPS 验证失败"""
        with patch('helper.validator.head') as mock_head:
            mock_head.side_effect = Exception("SSL error")

            result = httpsTimeOutValidator("192.168.1.1:8080")
            assert result is False
