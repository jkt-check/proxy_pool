# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testProxyPool
   Description :   入口模块单元测试
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
from click.testing import CliRunner


class TestProxyPoolCLI:
    """测试 proxyPool.py CLI"""

    def test_cli_schedule_command(self):
        """测试 schedule 命令"""
        from proxyPool import cli

        runner = CliRunner()

        with patch('proxyPool.startScheduler') as mock_start:
            mock_start.side_effect = KeyboardInterrupt()  # 防止阻塞

            result = runner.invoke(cli, ['schedule'])
            # 调用过 startScheduler
            mock_start.assert_called_once()

    def test_cli_server_command(self):
        """测试 server 命令"""
        from proxyPool import cli

        runner = CliRunner()

        with patch('proxyPool.startServer') as mock_start:
            mock_start.side_effect = KeyboardInterrupt()  # 防止阻塞

            result = runner.invoke(cli, ['server'])
            # 调用过 startServer
            mock_start.assert_called_once()

    def test_cli_version_option(self):
        """测试 --version 选项"""
        from proxyPool import cli

        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])

        assert '2.4.0' in result.output

    def test_cli_help_option(self):
        """测试 --help 选项"""
        from proxyPool import cli

        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert 'schedule' in result.output
        assert 'server' in result.output

    def test_cli_schedule_help(self):
        """测试 schedule --help"""
        from proxyPool import cli

        runner = CliRunner()
        result = runner.invoke(cli, ['schedule', '--help'])

        assert result.exit_code == 0

    def test_cli_server_help(self):
        """测试 server --help"""
        from proxyPool import cli

        runner = CliRunner()
        result = runner.invoke(cli, ['server', '--help'])

        assert result.exit_code == 0
