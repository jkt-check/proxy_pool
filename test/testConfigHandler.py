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
import tempfile
import pytest
from unittest.mock import patch
from handler.configHandler import ConfigHandler
from util.singleton import Singleton as _Singleton


def _reset_config():
    """清除 ConfigHandler 单例缓存"""
    _Singleton._inst.pop(ConfigHandler, None)


class TestConfigHandlerTypes:
    """测试 ConfigHandler 类型一致性"""

    def test_server_port_is_int(self):
        """
        RED: serverPort 应返回 int 类型
        """
        _reset_config()

        conf = ConfigHandler()
        port = conf.serverPort
        assert isinstance(port, int), f"serverPort 应为 int 类型，实际为 {type(port)}"
        assert port > 0, f"serverPort 应为正数，实际为 {port}"

    def test_server_host_is_string(self):
        """serverHost 应返回 str 类型"""
        _reset_config()

        conf = ConfigHandler()
        host = conf.serverHost
        assert isinstance(host, str), f"serverHost 应为 str 类型，实际为 {type(host)}"

    def test_verify_timeout_is_int(self):
        """verifyTimeout 应返回 int 类型"""
        _reset_config()

        conf = ConfigHandler()
        timeout = conf.verifyTimeout
        assert isinstance(timeout, int), f"verifyTimeout 应为 int 类型，实际为 {type(timeout)}"

    def test_max_fail_count_is_int(self):
        """maxFailCount 应返回 int 类型"""
        _reset_config()

        conf = ConfigHandler()
        count = conf.maxFailCount
        assert isinstance(count, int), f"maxFailCount 应为 int 类型，实际为 {type(count)}"

    def test_pool_size_min_is_int(self):
        """poolSizeMin 应返回 int 类型"""
        _reset_config()

        conf = ConfigHandler()
        size = conf.poolSizeMin
        assert isinstance(size, int), f"poolSizeMin 应为 int 类型，实际为 {type(size)}"

    def test_port_from_env_is_int(self):
        """
        RED: 从环境变量读取的 PORT 也应为 int 类型
        """
        _reset_config()

        with patch.dict(os.environ, {"PORT": "8888"}):
            import importlib
            import handler.configHandler as ch_module
            importlib.reload(ch_module)
            _Singleton._inst.pop(ch_module.ConfigHandler, None)

            conf = ch_module.ConfigHandler()
            port = conf.serverPort
            assert isinstance(port, int), f"从环境变量读取的 PORT 应为 int 类型，实际为 {type(port)}"
            assert port == 8888

    def test_db_conn_is_string(self):
        """dbConn 应返回 str 类型"""
        _reset_config()

        conf = ConfigHandler()
        db_conn = conf.dbConn
        assert isinstance(db_conn, str), f"dbConn 应为 str 类型，实际为 {type(db_conn)}"


class TestConfigHandlerYamlPriority:
    """测试 ConfigHandler 三级优先级：环境变量 > YAML > setting.py 默认值"""

    ENV_KEY = "PROXY_POOL_CONFIG"

    def _write_yaml(self, content: str) -> str:
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        f.write(content)
        f.close()
        return f.name

    def _cleanup_yaml(self, path: str):
        if os.path.exists(path):
            os.unlink(path)
        os.environ.pop(self.ENV_KEY, None)

    def test_yaml_overrides_default(self):
        """YAML 配置覆盖 setting.py 默认值"""
        yaml_path = self._write_yaml('host: "1.2.3.4"\nport: 9999\nverify_timeout: 30\n')
        os.environ[self.ENV_KEY] = yaml_path

        # 清除 env 污染
        for key in ["HOST", "PORT", "VERIFY_TIMEOUT"]:
            os.environ.pop(key, None)

        try:
            _reset_config()
            conf = ConfigHandler()
            assert conf.serverHost == "1.2.3.4"
            assert conf.serverPort == 9999
            assert conf.verifyTimeout == 30
        finally:
            self._cleanup_yaml(yaml_path)

    def test_env_overrides_yaml(self):
        """环境变量优先于 YAML 配置"""
        yaml_path = self._write_yaml('host: "1.2.3.4"\nport: 9999\n')
        os.environ[self.ENV_KEY] = yaml_path
        os.environ["HOST"] = "5.6.7.8"
        os.environ["PORT"] = "7777"

        try:
            _reset_config()
            conf = ConfigHandler()
            assert conf.serverHost == "5.6.7.8"
            assert conf.serverPort == 7777
        finally:
            self._cleanup_yaml(yaml_path)
            del os.environ["HOST"]
            del os.environ["PORT"]

    def test_default_when_no_yaml_no_env(self):
        """无 YAML 无环境变量时使用 setting.py 默认值"""
        os.environ.pop(self.ENV_KEY, None)
        for key in ["HOST", "PORT", "DB_CONN", "VERIFY_TIMEOUT", "PROXY_REGION"]:
            os.environ.pop(key, None)

        _reset_config()
        conf = ConfigHandler()
        import setting
        assert conf.serverHost == setting.HOST
        assert conf.serverPort == setting.PORT
        assert conf.verifyTimeout == setting.VERIFY_TIMEOUT

    def test_fetchers_from_yaml_list(self):
        """YAML 中 fetchers 为列表时正确加载"""
        yaml_path = self._write_yaml('proxy_fetcher:\n  - freeProxy01\n  - freeProxy03\n')
        os.environ[self.ENV_KEY] = yaml_path
        os.environ.pop("PROXY_FETCHER", None)

        try:
            _reset_config()
            conf = ConfigHandler()
            assert conf.fetchers == ["freeProxy01", "freeProxy03"]
        finally:
            self._cleanup_yaml(yaml_path)

    def test_fetchers_from_env_comma_separated(self):
        """环境变量 PROXY_FETCHER 逗号分隔优先于 YAML"""
        yaml_path = self._write_yaml('proxy_fetcher:\n  - freeProxy01\n')
        os.environ[self.ENV_KEY] = yaml_path
        os.environ["PROXY_FETCHER"] = "freeProxy05,freeProxy07"

        try:
            _reset_config()
            conf = ConfigHandler()
            assert conf.fetchers == ["freeProxy05", "freeProxy07"]
        finally:
            self._cleanup_yaml(yaml_path)
            del os.environ["PROXY_FETCHER"]

    def test_proxy_region_from_yaml_bool(self):
        """YAML 中 proxy_region 为 native bool 时正确解析"""
        yaml_path = self._write_yaml('proxy_region: false\n')
        os.environ[self.ENV_KEY] = yaml_path
        os.environ.pop("PROXY_REGION", None)

        try:
            _reset_config()
            conf = ConfigHandler()
            assert conf.proxyRegion is False
        finally:
            self._cleanup_yaml(yaml_path)

    def test_proxy_region_from_env_string(self):
        """环境变量 PROXY_REGION=False 正确解析为 False"""
        os.environ.pop(self.ENV_KEY, None)
        os.environ["PROXY_REGION"] = "False"

        try:
            _reset_config()
            conf = ConfigHandler()
            assert conf.proxyRegion is False
        finally:
            del os.environ["PROXY_REGION"]


class TestConfigHandlerConverterFallback:
    """测试 _get() converter 错误降级行为"""

    ENV_KEY = "PROXY_POOL_CONFIG"

    def _write_yaml(self, content: str) -> str:
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        f.write(content)
        f.close()
        return f.name

    def _cleanup_yaml(self, path: str):
        if os.path.exists(path):
            os.unlink(path)
        os.environ.pop(self.ENV_KEY, None)

    def test_invalid_env_int_falls_to_default(self):
        """环境变量 PORT=abc 转换失败时降级到默认值"""
        os.environ.pop(self.ENV_KEY, None)
        os.environ["PORT"] = "abc"

        try:
            _reset_config()
            conf = ConfigHandler()
            import setting
            assert conf.serverPort == setting.PORT  # 降级到 setting.py 默认值
        finally:
            del os.environ["PORT"]

    def test_invalid_env_bool_falls_to_default(self):
        """环境变量 PROXY_REGION=enabled 转换失败时降级到默认值"""
        os.environ.pop(self.ENV_KEY, None)
        os.environ["PROXY_REGION"] = "enabled"

        try:
            _reset_config()
            conf = ConfigHandler()
            import setting
            assert conf.proxyRegion == setting.PROXY_REGION  # 降级到 setting.py 默认值
        finally:
            del os.environ["PROXY_REGION"]

    def test_invalid_yaml_int_falls_to_default(self):
        """YAML port 非数字时降级到默认值"""
        yaml_path = self._write_yaml('port: "not_a_number"\n')
        os.environ[self.ENV_KEY] = yaml_path
        os.environ.pop("PORT", None)

        try:
            _reset_config()
            conf = ConfigHandler()
            import setting
            assert conf.serverPort == setting.PORT
        finally:
            self._cleanup_yaml(yaml_path)

    def test_invalid_yaml_bool_falls_to_default(self):
        """YAML proxy_region 无效字符串时降级到默认值"""
        yaml_path = self._write_yaml('proxy_region: "maybe"\n')
        os.environ[self.ENV_KEY] = yaml_path
        os.environ.pop("PROXY_REGION", None)

        try:
            _reset_config()
            conf = ConfigHandler()
            import setting
            assert conf.proxyRegion == setting.PROXY_REGION
        finally:
            self._cleanup_yaml(yaml_path)
