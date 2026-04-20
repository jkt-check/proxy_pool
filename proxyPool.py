# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxy_pool
   Description :   proxy pool 启动入口
   Author :        JHao
   date：          2020/6/19
-------------------------------------------------
   Change Activity:
                   2020/6/19:
                   2026/4/20: 添加 --config 选项
-------------------------------------------------
"""
__author__ = 'JHao'

import click
from helper.launcher import startServer, startScheduler
from setting import BANNER, VERSION
from util.yamlConfig import set_config_path

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=VERSION)
@click.option('--config', '-c', default=None,
              type=click.Path(exists=True, dir_okay=False),
              help='指定 YAML 配置文件路径')
@click.pass_context
def cli(ctx, config):
    """ProxyPool cli工具"""
    if config:
        set_config_path(config)


@cli.command(name="schedule")
def schedule():
    """ 启动调度程序 """
    click.echo(BANNER)
    startScheduler()


@cli.command(name="server")
def server():
    """ 启动api服务 """
    click.echo(BANNER)
    startServer()


if __name__ == '__main__':
    cli()
