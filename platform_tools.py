#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import platform


def is_mac():
    return platform.system() == 'Darwin'


def is_win():
    return platform.system() == 'Windows'


def is_linux():
    return platform.system() == 'Linux'


