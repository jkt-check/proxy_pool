# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     configUtils
   Description :   配置工具函数
   Author :        JHao
   date：          2026/4/20
-------------------------------------------------
   Change Activity:
                   2026/4/20: 添加 parse_bool 修复 proxyRegion bug
-------------------------------------------------
"""
__author__ = 'JHao'


_TRUE_VALUES = {"true", "1", "yes", "on"}
_FALSE_VALUES = {"false", "0", "no", "off"}


def parse_bool(value) -> bool:
    """将字符串或布尔值正确解析为 bool

    修复 bool("False") 为 True 的 bug：
    - bool 值直接返回
    - true/1/yes/on -> True（不区分大小写）
    - false/0/no/off -> False（不区分大小写）
    - 整数仅接受 0 和 1
    - 其他值抛出 ValueError
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value == 0:
            return False
        if value == 1:
            return True
        raise ValueError(f"Cannot parse bool from int: {value}")
    if isinstance(value, str):
        lower = value.strip().lower()
        if lower in _TRUE_VALUES:
            return True
        if lower in _FALSE_VALUES:
            return False
        raise ValueError(f"Cannot parse bool from string: {value!r}")
    raise ValueError(f"Cannot parse bool from {type(value).__name__}: {value!r}")