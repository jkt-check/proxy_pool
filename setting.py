# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setting.py
   Description :   配置文件
   Author :        JHao
   date：          2019/2/15
-------------------------------------------------
   Change Activity:
                   2019/2/15:
                   2024/4/19: 添加调度器配置项
-------------------------------------------------
"""

BANNER = r"""
****************************************************************
*** ______  ********************* ______ *********** _  ********
*** | ___ \_ ******************** | ___ \ ********* | | ********
*** | |_/ / \__ __   __  _ __   _ | |_/ /___ * ___  | | ********
*** |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | | ********
*** | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___  ****
*** \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____/ ****
****                       __ / /                          *****
************************* /___ / *******************************
*************************       ********************************
****************************************************************
"""

VERSION = "2.4.0"

# ############### server config ###############
# API 服务绑定地址
HOST = "0.0.0.0"

# API 服务端口
PORT = 5010

# ############### database config ###################
# db connection uri
# example:
#      Redis: redis://:password@ip:port/db
#      SSDB:  ssdb://:password@ip:port
DB_CONN = 'redis://:<password>@127.0.0.1:6379/0'

# proxy table name
TABLE_NAME = 'use_proxy'


# ###### config the proxy fetch function ######
PROXY_FETCHER = [
    "freeProxy01",
    "freeProxy02",
    "freeProxy03",
    "freeProxy04",
    "freeProxy05",
    "freeProxy06",
    "freeProxy07",
    "freeProxy08",
    "freeProxy09",
    "freeProxy10",
    "freeProxy11"
]

# ############# proxy validator #################
# 代理验证目标网站
# 用于验证代理是否能正常访问 HTTP/HTTPS 网站
HTTP_URL = "http://httpbin.org"

HTTPS_URL = "https://www.qq.com"

# 代理验证时超时时间（秒）
VERIFY_TIMEOUT = 10

# 近期检查中允许的最大失败次数，超过则剔除代理
# 设为 0 表示只要有 1 次失败就剔除
MAX_FAIL_COUNT = 0

# 近PROXY_CHECK_COUNT次校验中允许的最大失败率,超过则剔除代理
# MAX_FAIL_RATE = 0.1

# 代理检查时代理数量少于此值触发抓取
POOL_SIZE_MIN = 20

# ############# proxy attributes #################
# 是否启用代理地域属性
# True: 获取代理 IP 的地理位置信息（通过 CSDN API）
# False: 不获取地域信息，可提高验证速度
PROXY_REGION = True

# ############# scheduler config #################
# 代理抓取间隔（分钟）
# 建议: 3-10 分钟，过频可能被代理网站封禁
SCHEDULER_FETCH_INTERVAL = 4

# 代理检查间隔（分钟）
# 建议: 2-5 分钟，确保代理池中代理可用性
SCHEDULER_CHECK_INTERVAL = 2

# 代理检查线程数
# 建议: 10-50，根据服务器性能调整
CHECKER_THREAD_COUNT = 20

# Set the timezone for the scheduler forcely (optional)
# If it is running on a VM, and
#   "ValueError: Timezone offset does not match system offset"
#   was raised during scheduling.
# Please uncomment the following line and set a timezone for the scheduler.
# Otherwise it will detect the timezone from the system automatically.

TIMEZONE = "Asia/Shanghai"
