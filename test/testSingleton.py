# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testSingleton
   Description :   Singleton 单元测试
   Author :        JHao
   date：          2024/4/19
-------------------------------------------------
   Change Activity:
                   2024/4/19: TDD 测试
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from util.singleton import Singleton


class TestSingleton:
    """测试 Singleton 元类"""

    def test_singleton_returns_same_instance(self):
        """Singleton 应返回相同实例"""
        class TestClass(metaclass=Singleton):
            def __init__(self):
                self.value = 0

        instance1 = TestClass()
        instance2 = TestClass()
        assert instance1 is instance2

    def test_singleton_supports_args(self):
        """Singleton 应支持位置参数"""
        class TestClassArgs(metaclass=Singleton):
            def __init__(self, value):
                self.value = value

        instance = TestClassArgs(42)
        assert instance.value == 42

    def test_singleton_supports_kwargs(self):
        """
        RED: Singleton 应支持关键字参数
        """
        class TestClassKwargs(metaclass=Singleton):
            def __init__(self, name="default", count=0):
                self.name = name
                self.count = count

        instance = TestClassKwargs(name="test", count=10)
        assert instance.name == "test"
        assert instance.count == 10

    def test_singleton_kwargs_first_call_wins(self):
        """第一次调用的参数应该保留"""
        class TestClassFirstWins(metaclass=Singleton):
            def __init__(self, value=0):
                self.value = value

        instance1 = TestClassFirstWins(value=100)
        instance2 = TestClassFirstWins(value=200)  # 第二次调用被忽略
        assert instance1 is instance2
        assert instance1.value == 100

    def test_singleton_mixed_args_and_kwargs(self):
        """应支持混合位置和关键字参数"""
        class TestClassMixed(metaclass=Singleton):
            def __init__(self, a, b=10, c=20):
                self.a = a
                self.b = b
                self.c = c

        instance = TestClassMixed(1, b=2, c=3)
        assert instance.a == 1
        assert instance.b == 2
        assert instance.c == 3
