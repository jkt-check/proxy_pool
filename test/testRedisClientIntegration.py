# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testRedisClientIntegration
   Description :   Redis 客户端集成测试（需本地 Redis）
   Author :        JHao
   date：          2024/4/19
-------------------------------------------------
   Change Activity:
                   2024/4/19: TDD 测试
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
import json
from helper.proxy import Proxy


# 检查 Redis 是否可用
redis_available = False
try:
    import redis
    client = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=2)
    client.ping()
    redis_available = True
except:
    pass


@pytest.mark.skipif(not redis_available, reason="需要本地 Redis 服务运行")
class TestRedisClient:
    """测试 Redis 客户端"""

    def test_put_and_get(self):
        """测试存入和获取代理"""
        from db.redisClient import RedisClient
        client = RedisClient(host="127.0.0.1", port=6379, db=0)
        client.changeTable("test_proxy")
        client.clear()

        proxy = Proxy("192.168.1.1:8080", source="test")
        client.put(proxy)

        result = client.get(https=False)
        assert result is not None
        data = json.loads(result)
        assert "192.168.1.1:8080" in data.get("proxy", "")

        client.clear()

    def test_exists(self):
        """测试代理是否存在"""
        from db.redisClient import RedisClient
        client = RedisClient(host="127.0.0.1", port=6379, db=0)
        client.changeTable("test_proxy")
        client.clear()

        proxy = Proxy("192.168.1.2:8080", source="test")
        client.put(proxy)

        assert client.exists("192.168.1.2:8080") is True
        assert client.exists("192.168.1.3:8080") is False

        client.clear()

    def test_delete(self):
        """测试删除代理"""
        from db.redisClient import RedisClient
        client = RedisClient(host="127.0.0.1", port=6379, db=0)
        client.changeTable("test_proxy")
        client.clear()

        proxy = Proxy("192.168.1.3:8080", source="test")
        client.put(proxy)

        assert client.exists("192.168.1.3:8080") is True
        client.delete("192.168.1.3:8080")
        assert client.exists("192.168.1.3:8080") is False

    def test_get_all(self):
        """测试获取所有代理"""
        from db.redisClient import RedisClient
        client = RedisClient(host="127.0.0.1", port=6379, db=0)
        client.changeTable("test_proxy")
        client.clear()

        proxy1 = Proxy("192.168.1.4:8080", source="test")
        proxy2 = Proxy("192.168.1.5:8080", source="test", https=True)
        client.put(proxy1)
        client.put(proxy2)

        all_proxies = client.getAll(https=False)
        assert len(all_proxies) >= 2

        https_proxies = client.getAll(https=True)
        assert len(https_proxies) >= 1

        client.clear()

    def test_pop(self):
        """测试弹出代理"""
        from db.redisClient import RedisClient
        client = RedisClient(host="127.0.0.1", port=6379, db=0)
        client.changeTable("test_proxy")
        client.clear()

        proxy = Proxy("192.168.1.6:8080", source="test")
        client.put(proxy)

        result = client.pop(https=False)
        assert result is not None
        # 弹出后不应存在
        assert client.exists("192.168.1.6:8080") is False

    def test_get_count(self):
        """测试获取代理数量"""
        from db.redisClient import RedisClient
        client = RedisClient(host="127.0.0.1", port=6379, db=0)
        client.changeTable("test_proxy")
        client.clear()

        proxy1 = Proxy("192.168.1.8:8080", source="test")
        proxy2 = Proxy("192.168.1.9:8080", source="test", https=True)
        client.put(proxy1)
        client.put(proxy2)

        count = client.getCount()
        assert count['total'] >= 2
        assert count['https'] >= 1

        client.clear()

    def test_clear(self):
        """测试清空代理"""
        from db.redisClient import RedisClient
        client = RedisClient(host="127.0.0.1", port=6379, db=0)
        client.changeTable("test_proxy")

        proxy = Proxy("192.168.1.10:8080", source="test")
        client.put(proxy)

        client.clear()
        count = client.getCount()
        assert count['total'] == 0

    def test_change_table(self):
        """测试切换表"""
        from db.redisClient import RedisClient
        client = RedisClient(host="127.0.0.1", port=6379, db=0)
        client.changeTable("test_proxy_2")
        client.clear()

        proxy = Proxy("192.168.1.11:8080", source="test")
        client.put(proxy)

        assert client.exists("192.168.1.11:8080") is True

        # 切换回原表
        client.changeTable("test_proxy")
        assert client.exists("192.168.1.11:8080") is False

        # 清理
        client.changeTable("test_proxy_2")
        client.clear()
