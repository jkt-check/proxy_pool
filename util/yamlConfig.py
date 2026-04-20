# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     yamlConfig
   Description :   YAML 配置文件加载
   Author :        JHao
   date：          2026/4/20
-------------------------------------------------
   Change Activity:
                   2026/4/20: 支持 YAML 配置文件
-------------------------------------------------
"""
__author__ = 'JHao'

import logging
import os

import yaml

_logger = logging.getLogger(__name__)

_CONFIG_ENV_KEY = "PROXY_POOL_CONFIG"

_DEFAULT_CONFIG_PATHS = [
    "config.yaml",
    "/etc/proxy-pool/config.yaml",
]


def set_config_path(path: str) -> None:
    """存储配置文件路径到环境变量（CLI 调用）"""
    os.environ[_CONFIG_ENV_KEY] = path


def _find_config_file() -> str | None:
    """按优先级查找配置文件：环境变量 > 默认路径"""
    env_path = os.environ.get(_CONFIG_ENV_KEY)
    if env_path:
        if os.path.isfile(env_path):
            return env_path
        _logger.warning("PROXY_POOL_CONFIG=%s 指定的配置文件不存在", env_path)
        return None

    for path in _DEFAULT_CONFIG_PATHS:
        if os.path.isfile(path):
            return path

    return None


def load_yaml_config() -> dict:
    """加载 YAML 配置文件，返回 dict，失败返回空 dict"""
    config_path = _find_config_file()
    if not config_path:
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except yaml.YAMLError as e:
        _logger.warning("YAML 配置文件解析失败 %s: %s", config_path, e)
        return {}
    except OSError as e:
        _logger.warning("YAML 配置文件读取失败 %s: %s", config_path, e)
        return {}
    except UnicodeDecodeError as e:
        _logger.warning("YAML 配置文件编码错误 %s: %s", config_path, e)
        return {}