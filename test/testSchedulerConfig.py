# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testScheduler
   Description :   Scheduler 配置单元测试
   Author :        JHao
   date：          2024/4/19
-------------------------------------------------
   Change Activity:
                   2024/4/19: TDD 测试魔术数字配置化
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from handler.configHandler import ConfigHandler


class TestSchedulerConfig:
    """测试调度器配置"""

    def test_fetch_interval_exists(self):
        """
        RED: ConfigHandler 应有 fetchInterval 配置
        """
        conf = ConfigHandler()
        assert hasattr(conf, 'fetchInterval'), "ConfigHandler 应有 fetchInterval 属性"
        assert isinstance(conf.fetchInterval, int)
        assert conf.fetchInterval > 0

    def test_check_interval_exists(self):
        """
        RED: ConfigHandler 应有 checkInterval 配置
        """
        conf = ConfigHandler()
        assert hasattr(conf, 'checkInterval'), "ConfigHandler 应有 checkInterval 属性"
        assert isinstance(conf.checkInterval, int)
        assert conf.checkInterval > 0

    def test_checker_thread_count_exists(self):
        """
        RED: ConfigHandler 应有 checkerThreadCount 配置
        """
        conf = ConfigHandler()
        assert hasattr(conf, 'checkerThreadCount'), "ConfigHandler 应有 checkerThreadCount 属性"
        assert isinstance(conf.checkerThreadCount, int)
        assert conf.checkerThreadCount > 0

    def test_default_fetch_interval_is_reasonable(self):
        """默认抓取间隔应合理（分钟）"""
        conf = ConfigHandler()
        # 默认 4 分钟，应该在 1-60 分钟范围内
        assert 1 <= conf.fetchInterval <= 60

    def test_default_check_interval_is_reasonable(self):
        """默认检查间隔应合理（分钟）"""
        conf = ConfigHandler()
        # 默认 2 分钟，应该在 1-60 分钟范围内
        assert 1 <= conf.checkInterval <= 60

    def test_default_thread_count_is_reasonable(self):
        """默认线程数应合理"""
        conf = ConfigHandler()
        # 默认 20 个线程，应该在 1-100 范围内
        assert 1 <= conf.checkerThreadCount <= 100

    def test_fetch_interval_from_env(self):
        """
        RED: 应支持从环境变量读取 fetchInterval
        """
        import os
        from unittest.mock import patch
        from util.singleton import Singleton

        Singleton._inst.pop(ConfigHandler, None)

        with patch.dict(os.environ, {"SCHEDULER_FETCH_INTERVAL": "10"}):
            import importlib
            import handler.configHandler as ch_module
            importlib.reload(ch_module)
            Singleton._inst.pop(ch_module.ConfigHandler, None)

            conf = ch_module.ConfigHandler()
            assert conf.fetchInterval == 10
