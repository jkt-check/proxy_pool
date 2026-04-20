# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testYamlConfig
   Description :   yamlConfig 单元测试
   Author :        JHao
   date：          2026/4/20
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import tempfile

import pytest

from util.yamlConfig import load_yaml_config, set_config_path, _find_config_file, _CONFIG_ENV_KEY


class TestLoadYamlConfig:
    """load_yaml_config 函数测试"""

    def test_no_config_file_returns_empty_dict(self):
        """无配置文件时返回空 dict"""
        os.environ.pop(_CONFIG_ENV_KEY, None)
        result = load_yaml_config()
        assert result == {}

    def test_valid_yaml_file(self):
        """加载有效 YAML 文件"""
        yaml_content = "host: \"1.2.3.4\"\nport: 9999\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            config_path = f.name

        os.environ[_CONFIG_ENV_KEY] = config_path
        try:
            result = load_yaml_config()
            assert result == {"host": "1.2.3.4", "port": 9999}
        finally:
            os.unlink(config_path)
            del os.environ[_CONFIG_ENV_KEY]

    def test_empty_yaml_file_returns_empty_dict(self):
        """空 YAML 文件返回空 dict"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            config_path = f.name

        os.environ[_CONFIG_ENV_KEY] = config_path
        try:
            result = load_yaml_config()
            assert result == {}
        finally:
            os.unlink(config_path)
            del os.environ[_CONFIG_ENV_KEY]

    def test_malformed_yaml_returns_empty_dict(self):
        """格式错误的 YAML 返回空 dict"""
        yaml_content = "host: \"1.2.3.4\n  bad indent\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            config_path = f.name

        os.environ[_CONFIG_ENV_KEY] = config_path
        try:
            result = load_yaml_config()
            assert result == {}
        finally:
            os.unlink(config_path)
            del os.environ[_CONFIG_ENV_KEY]

    def test_yaml_with_list_value(self):
        """YAML 列表值正确加载"""
        yaml_content = "proxy_fetcher:\n  - freeProxy01\n  - freeProxy03\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            config_path = f.name

        os.environ[_CONFIG_ENV_KEY] = config_path
        try:
            result = load_yaml_config()
            assert result == {"proxy_fetcher": ["freeProxy01", "freeProxy03"]}
        finally:
            os.unlink(config_path)
            del os.environ[_CONFIG_ENV_KEY]

    def test_yaml_with_boolean_values(self):
        """YAML 布尔值正确加载（native bool）"""
        yaml_content = "proxy_region: false\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            config_path = f.name

        os.environ[_CONFIG_ENV_KEY] = config_path
        try:
            result = load_yaml_config()
            assert result == {"proxy_region": False}
        finally:
            os.unlink(config_path)
            del os.environ[_CONFIG_ENV_KEY]

    def test_yaml_top_level_list_returns_empty_dict(self):
        """YAML 顶层非 dict 类型返回空 dict"""
        yaml_content = "- item1\n- item2\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            config_path = f.name

        os.environ[_CONFIG_ENV_KEY] = config_path
        try:
            result = load_yaml_config()
            assert result == {}
        finally:
            os.unlink(config_path)
            del os.environ[_CONFIG_ENV_KEY]


class TestSetConfigPath:
    """set_config_path 函数测试"""

    def test_sets_env_variable(self):
        """set_config_path 设置环境变量"""
        os.environ.pop(_CONFIG_ENV_KEY, None)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("host: test\n")
            config_path = f.name

        try:
            set_config_path(config_path)
            assert os.environ.get(_CONFIG_ENV_KEY) == config_path
        finally:
            os.unlink(config_path)
            os.environ.pop(_CONFIG_ENV_KEY, None)

    def test_find_config_file_uses_env_var(self):
        """_find_config_file 优先使用环境变量"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("host: test\n")
            config_path = f.name

        os.environ[_CONFIG_ENV_KEY] = config_path
        try:
            result = _find_config_file()
            assert result == config_path
        finally:
            os.unlink(config_path)
            del os.environ[_CONFIG_ENV_KEY]

    def test_find_config_file_nonexistent_env_path(self):
        """环境变量指向不存在的文件时返回 None"""
        os.environ[_CONFIG_ENV_KEY] = "/nonexistent/path/config.yaml"
        try:
            result = _find_config_file()
            assert result is None
        finally:
            del os.environ[_CONFIG_ENV_KEY]