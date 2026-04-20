# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testConfigUtils
   Description :   configUtils 单元测试
   Author :        JHao
   date：          2026/4/20
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from util.configUtils import parse_bool


class TestParseBool:
    """parse_bool 函数测试"""

    # bool 输入直接返回
    @pytest.mark.parametrize("value,expected", [
        (True, True),
        (False, False),
    ])
    def test_bool_input(self, value, expected):
        assert parse_bool(value) is expected

    # 字符串 true 值
    @pytest.mark.parametrize("value", ["true", "True", "TRUE", "1", "yes", "Yes", "on", "ON"])
    def test_true_strings(self, value):
        assert parse_bool(value) is True

    # 字符串 false 值
    @pytest.mark.parametrize("value", ["false", "False", "FALSE", "0", "no", "No", "off", "OFF"])
    def test_false_strings(self, value):
        assert parse_bool(value) is False

    # 带空格的字符串
    def test_string_with_whitespace(self):
        assert parse_bool("  true  ") is True
        assert parse_bool("  false  ") is False

    # 整数 0 和 1
    def test_int_zero(self):
        assert parse_bool(0) is False

    def test_int_one(self):
        assert parse_bool(1) is True

    # 无法识别的字符串应抛出 ValueError
    @pytest.mark.parametrize("value", ["maybe", "enabled", "disabled", "2", "abc"])
    def test_invalid_string_raises(self, value):
        with pytest.raises(ValueError):
            parse_bool(value)

    # 非 0/1 整数应抛出 ValueError
    @pytest.mark.parametrize("value", [2, -1, 999])
    def test_invalid_int_raises(self, value):
        with pytest.raises(ValueError):
            parse_bool(value)

    # 其他类型应抛出 ValueError
    def test_invalid_type_raises(self):
        with pytest.raises(ValueError):
            parse_bool(3.14)

    # 关键回归测试：bool("False") 之前为 True 的 bug
    def test_regression_bool_false_string(self):
        assert parse_bool("False") is False