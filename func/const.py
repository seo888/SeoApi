# -*- coding: UTF-8 -*-
"""常量配置"""

from enum import Enum


class BaiduAction(str, Enum):
    """百度接口数据限制"""
    SOURCE = "source"
    DATA = "data"
    INCLUDED = "included"
    INCLUDE = "include"
    PULLDOWN = "pulldown"


class GoogleAction(str, Enum):
    """谷歌接口数据限制"""
    SOURCE = "source"
    DATA = "data"
    INCLUDE = "include"
    PULLDOWN = "pulldown"

class BingAction(str, Enum):
    """必应接口数据限制"""
    SOURCE = "source"
    DATA = "data"
    INCLUDE = "include"
    INCLUDE_NEXT = "include_next"
    PULLDOWN = "pulldown"


class Mir6Action(str, Enum):
    """mir6接口数据限制"""
    WEIGHT = "weight"

class DomainAction(str, Enum):
    """mir6接口数据限制"""
    DOMAIN = "domain"

class DomainsAction(str, Enum):
    """domains数据限制"""
    LOG = "log"
    REGISTER = "register"
