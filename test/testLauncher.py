# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testLauncher
   Description :   Launcher 模块单元测试
   Author :        JHao
   date：          2024/4/19
-------------------------------------------------
   Change Activity:
                   2024/4/19: TDD 测试
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest


class TestLauncher:
    """测试 Launcher 模块"""

    def test_start_server_exists(self):
        """测试 startServer 函数存在"""
        from helper import launcher
        assert hasattr(launcher, 'startServer')
        assert callable(launcher.startServer)

    def test_start_scheduler_exists(self):
        """测试 startScheduler 函数存在"""
        from helper import launcher
        assert hasattr(launcher, 'startScheduler')
        assert callable(launcher.startScheduler)

    def test_launcher_imports(self):
        """测试 launcher 导入依赖"""
        from helper import launcher
        assert hasattr(launcher, 'DbClient')
        assert hasattr(launcher, 'LogHandler')
        assert hasattr(launcher, 'ConfigHandler')
