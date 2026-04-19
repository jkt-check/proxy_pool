# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testScheduler
   Description :   Scheduler 模块单元测试
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


class TestSchedulerFunctions:
    """测试调度器函数"""

    def test_run_scheduler_adds_jobs(self):
        """测试调度器添加任务"""
        from helper.scheduler import runScheduler

        with patch('helper.scheduler.BlockingScheduler') as mock_scheduler_class:
            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            # 模拟 start 阻塞
            mock_scheduler.start.side_effect = KeyboardInterrupt()

            with pytest.raises(KeyboardInterrupt):
                runScheduler()

            # 验证添加了两个任务
            assert mock_scheduler.add_job.call_count == 2

    def test_scheduler_config_used(self):
        """测试调度器使用配置"""
        from handler.configHandler import ConfigHandler
        conf = ConfigHandler()

        # 验证调度器配置存在
        assert hasattr(conf, 'fetchInterval')
        assert hasattr(conf, 'checkInterval')
        assert conf.fetchInterval > 0
        assert conf.checkInterval > 0
