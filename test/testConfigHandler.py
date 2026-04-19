# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testConfigHandler
   Description :   ConfigHandler 单元测试
   Author :        JHao
   date：          2024/4/19
-------------------------------------------------
   Change Activity:
                   2024/4/19: TDD 测试端口类型一致性
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import pytest
from unittest.mock import patch
from handler.configHandler import ConfigHandler


class TestConfigHandlerTypes:
    """测试 ConfigHandler 类型一致性"""

    def test_server_port_is_int(self):
        """
        RED: serverPort 应返回 int 类型
        """
        # 清除单例缓存以重新加载配置
        from util.singleton import Singleton
        Singleton._inst.pop(ConfigHandler, None)

        conf = ConfigHandler()
        port = conf.serverPort
        assert isinstance(port, int), f"serverPort 应为 int 类型，实际为 {type(port)}"
        assert port > 0, f"serverPort 应为正数，实际为 {port}"

    def test_server_host_is_string(self):
        """serverHost 应返回 str 类型"""
        from util.singleton import Singleton
        Singleton._inst.pop(ConfigHandler, None)

        conf = ConfigHandler()
        host = conf.serverHost
        assert isinstance(host, str), f"serverHost 应为 str 类型，实际为 {type(host)}"

    def test_verify_timeout_is_int(self):
        """verifyTimeout 应返回 int 类型"""
        from util.singleton import Singleton
        Singleton._inst.pop(ConfigHandler, None)

        conf = ConfigHandler()
        timeout = conf.verifyTimeout
        assert isinstance(timeout, int), f"verifyTimeout 应为 int 类型，实际为 {type(timeout)}"

    def test_max_fail_count_is_int(self):
        """maxFailCount 应返回 int 类型"""
        from util.singleton import Singleton
        Singleton._inst.pop(ConfigHandler, None)

        conf = ConfigHandler()
        count = conf.maxFailCount
        assert isinstance(count, int), f"maxFailCount 应为 int 类型，实际为 {type(count)}"

    def test_pool_size_min_is_int(self):
        """poolSizeMin 应返回 int 类型"""
        from util.singleton import Singleton
        Singleton._inst.pop(ConfigHandler, None)

        conf = ConfigHandler()
        size = conf.poolSizeMin
        assert isinstance(size, int), f"poolSizeMin 应为 int 类型，实际为 {type(size)}"

    def test_port_from_env_is_int(self):
        """
        RED: 从环境变量读取的 PORT 也应为 int 类型
        """
        from util.singleton import Singleton
        Singleton._inst.pop(ConfigHandler, None)

        with patch.dict(os.environ, {"PORT": "8888"}):
            # 强制重新加载
            import importlib
            import handler.configHandler as ch_module
            importlib.reload(ch_module)
            Singleton._inst.pop(ch_module.ConfigHandler, None)

            conf = ch_module.ConfigHandler()
            port = conf.serverPort
            assert isinstance(port, int), f"从环境变量读取的 PORT 应为 int 类型，实际为 {type(port)}"
            assert port == 8888

    def test_db_conn_is_string(self):
        """dbConn 应返回 str 类型"""
        from util.singleton import Singleton
        Singleton._inst.pop(ConfigHandler, None)

        conf = ConfigHandler()
        db_conn = conf.dbConn
        assert isinstance(db_conn, str), f"dbConn 应为 str 类型，实际为 {type(db_conn)}"


def testConfig():
    """
    原有测试函数
    :return:
    """
    from util.singleton import Singleton
    Singleton._inst.pop(ConfigHandler, None)

    conf = ConfigHandler()
    print(conf.dbConn)
    print(conf.serverPort)
    print(conf.serverHost)
    print(conf.tableName)
    assert isinstance(conf.fetchers, list)
    print(conf.fetchers)


if __name__ == '__main__':
    testConfig()
