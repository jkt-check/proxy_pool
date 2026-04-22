# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     configHandler
   Description :
   Author :        JHao
   date：          2020/6/22
-------------------------------------------------
   Change Activity:
                   2020/6/22:
                   2024/4/19: 修复端口类型不一致问题
                   2026/4/20: 支持 YAML 配置文件，三级优先级
-------------------------------------------------
"""
__author__ = 'JHao'

import logging
import os
import setting
from util.singleton import Singleton
from util.lazyProperty import LazyProperty
from util.six import withMetaclass
from util.yamlConfig import load_yaml_config
from util.configUtils import parse_bool

_logger = logging.getLogger(__name__)

# 配置属性映射：(环境变量key, YAML key, 类型转换)
# 类型转换: None=原样返回, int=int, parse_bool=布尔解析
_CONFIG_MAP = {
    "serverHost":       ("HOST", "host", None),
    "serverPort":       ("PORT", "port", int),
    "dbConn":           ("DB_CONN", "db_conn", None),
    "tableName":        ("TABLE_NAME", "table_name", None),
    "httpUrl":          ("HTTP_URL", "http_url", None),
    "httpsUrl":         ("HTTPS_URL", "https_url", None),
    "verifyTimeout":    ("VERIFY_TIMEOUT", "verify_timeout", int),
    "maxFailCount":     ("MAX_FAIL_COUNT", "max_fail_count", int),
    "poolSizeMin":      ("POOL_SIZE_MIN", "pool_size_min", int),
    "proxyRegion":      ("PROXY_REGION", "proxy_region", parse_bool),
    "timezone":         ("TIMEZONE", "timezone", None),
    "fetchers":         ("PROXY_FETCHER", "proxy_fetcher", None),
    "fetchInterval":    ("SCHEDULER_FETCH_INTERVAL", "scheduler_fetch_interval", int),
    "checkInterval":    ("SCHEDULER_CHECK_INTERVAL", "scheduler_check_interval", int),
    "checkerThreadCount": ("CHECKER_THREAD_COUNT", "checker_thread_count", int),
    "refreshSignalKey": ("REFRESH_SIGNAL_KEY", "refresh_signal_key", None),
}


class ConfigHandler(withMetaclass(Singleton)):

    def __init__(self):
        self._yaml_config = None  # 延迟加载，确保 set_config_path() 先执行

    @property
    def yaml_config(self):
        """延迟加载 YAML 配置，确保 CLI --config 选项先生效"""
        if self._yaml_config is None:
            self._yaml_config = load_yaml_config()
        return self._yaml_config

    def _get(self, env_key: str, yaml_key: str, default, converter=None):
        """三级优先级：环境变量 > YAML 配置文件 > setting.py 默认值"""
        # 1. 环境变量
        env_value = os.environ.get(env_key)
        if env_value is not None:
            if env_value == "":
                _logger.warning("环境变量 %s 为空字符串，已忽略", env_key)
            elif converter is not None:
                try:
                    return converter(env_value)
                except (ValueError, TypeError) as e:
                    _logger.warning("环境变量 %s=%s 转换失败: %s，将降级到下一优先级",
                                     env_key, env_value, e)
            else:
                return env_value

        # 2. YAML 配置文件（延迟加载）
        yaml_value = self.yaml_config.get(yaml_key)
        if yaml_value is not None:
            if converter is not None:
                # 防止 YAML 原生布尔被 int() 静默转换（如 port: yes -> int(True) == 1）
                if converter is int and isinstance(yaml_value, bool):
                    _logger.warning("YAML 配置 %s=%r 类型不匹配，期望整数，已忽略",
                                     yaml_key, yaml_value)
                else:
                    try:
                        return converter(yaml_value)
                    except (ValueError, TypeError) as e:
                        _logger.warning("YAML 配置 %s=%r 转换失败: %s，将降级到默认值",
                                         yaml_key, yaml_value, e)
            else:
                return yaml_value

        # 3. setting.py 默认值（已是正确类型，无需再转换）
        return default

    @LazyProperty
    def serverHost(self):
        env_key, yaml_key, converter = _CONFIG_MAP["serverHost"]
        return self._get(env_key, yaml_key, setting.HOST, converter)

    @LazyProperty
    def serverPort(self) -> int:
        """返回 int 类型的端口号"""
        env_key, yaml_key, converter = _CONFIG_MAP["serverPort"]
        return self._get(env_key, yaml_key, setting.PORT, converter)

    @LazyProperty
    def dbConn(self):
        env_key, yaml_key, converter = _CONFIG_MAP["dbConn"]
        return self._get(env_key, yaml_key, setting.DB_CONN, converter)

    @LazyProperty
    def tableName(self):
        env_key, yaml_key, converter = _CONFIG_MAP["tableName"]
        return self._get(env_key, yaml_key, setting.TABLE_NAME, converter)

    @LazyProperty
    def fetchers(self):
        """支持环境变量（逗号分隔）和 YAML list"""
        env_key, yaml_key, _ = _CONFIG_MAP["fetchers"]

        # 1. 环境变量
        env_value = os.environ.get(env_key)
        if env_value is not None:
            if env_value == "":
                _logger.warning("环境变量 %s 为空字符串，已忽略", env_key)
            else:
                return [s.strip() for s in env_value.split(",") if s.strip()]

        # 2. YAML 配置文件
        yaml_value = self.yaml_config.get(yaml_key)
        if yaml_value is not None:
            if isinstance(yaml_value, list):
                return yaml_value
            _logger.warning("YAML 配置 %s 应为列表类型，实际为 %s，已忽略",
                             yaml_key, type(yaml_value).__name__)

        # 3. setting.py 默认值
        return setting.PROXY_FETCHER

    @LazyProperty
    def httpUrl(self):
        env_key, yaml_key, converter = _CONFIG_MAP["httpUrl"]
        return self._get(env_key, yaml_key, setting.HTTP_URL, converter)

    @LazyProperty
    def httpsUrl(self):
        env_key, yaml_key, converter = _CONFIG_MAP["httpsUrl"]
        return self._get(env_key, yaml_key, setting.HTTPS_URL, converter)

    @LazyProperty
    def verifyTimeout(self) -> int:
        env_key, yaml_key, converter = _CONFIG_MAP["verifyTimeout"]
        return self._get(env_key, yaml_key, setting.VERIFY_TIMEOUT, converter)

    @LazyProperty
    def maxFailCount(self) -> int:
        env_key, yaml_key, converter = _CONFIG_MAP["maxFailCount"]
        return self._get(env_key, yaml_key, setting.MAX_FAIL_COUNT, converter)

    @LazyProperty
    def poolSizeMin(self) -> int:
        env_key, yaml_key, converter = _CONFIG_MAP["poolSizeMin"]
        return self._get(env_key, yaml_key, setting.POOL_SIZE_MIN, converter)

    @LazyProperty
    def proxyRegion(self):
        env_key, yaml_key, converter = _CONFIG_MAP["proxyRegion"]
        return self._get(env_key, yaml_key, setting.PROXY_REGION, converter)

    @LazyProperty
    def timezone(self):
        env_key, yaml_key, converter = _CONFIG_MAP["timezone"]
        return self._get(env_key, yaml_key, setting.TIMEZONE, converter)

    # ############# scheduler config #################
    @LazyProperty
    def fetchInterval(self) -> int:
        """代理抓取间隔（分钟）"""
        env_key, yaml_key, converter = _CONFIG_MAP["fetchInterval"]
        return self._get(env_key, yaml_key, setting.SCHEDULER_FETCH_INTERVAL, converter)

    @LazyProperty
    def checkInterval(self) -> int:
        """代理检查间隔（分钟）"""
        env_key, yaml_key, converter = _CONFIG_MAP["checkInterval"]
        return self._get(env_key, yaml_key, setting.SCHEDULER_CHECK_INTERVAL, converter)

    @LazyProperty
    def checkerThreadCount(self) -> int:
        """代理检查线程数"""
        env_key, yaml_key, converter = _CONFIG_MAP["checkerThreadCount"]
        return self._get(env_key, yaml_key, setting.CHECKER_THREAD_COUNT, converter)

    @LazyProperty
    def refreshSignalKey(self):
        """API 触发刷新的 Redis 信号键名"""
        env_key, yaml_key, converter = _CONFIG_MAP["refreshSignalKey"]
        return self._get(env_key, yaml_key, setting.REFRESH_SIGNAL_KEY, converter)
