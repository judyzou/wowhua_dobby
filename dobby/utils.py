#!usr/bin/env python
# -*- coding: utf-8 -*-
from fabric.context_managers import settings, prefix
from fabric.state import env


VIRTUALENV = '/zch/virtualenvs/zchenv'


def zch():
    """
    run following commands as user `zch`
    zch need to be configed in /etc/sudoers
    %sudo   ALL=(zch) NOPASSWD: /bin/bash
    """
    return settings(sudo_user='zch')


def zchenv():
    """
    enter zchenv
    """
    return prefix('. {}/bin/activate'.format(VIRTUALENV))
