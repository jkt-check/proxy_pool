# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     singleton
   Description :
   Author :        JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3:
                   2024/4/19: 修复 kwargs 参数丢失问题
-------------------------------------------------
"""
__author__ = 'JHao'


class Singleton(type):
    """
    Singleton Metaclass
    """

    _inst = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._inst:
            cls._inst[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._inst[cls]
