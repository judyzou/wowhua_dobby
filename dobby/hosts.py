#!usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hosts definition.

for aws, adapt the implementation of get_hosts to dynamically load
running instances of each role
"""
from fabric.contrib.console import confirm
from fabric.utils import abort


_addresses = {
    'live': {
        'cron': ['202.85.216.122'],
        'admin': ['202.85.216.122'],
        'cms': ['202.85.216.121'],
        'api': ['202.85.208.98', '202.85.216.122']
    }
}


_platform_addresses = {
    'live': {
        'munin-master': ['202.85.216.121'],
    }
}


def get_hosts(env, role='all'):
    """
    get instance hosts of a role in a given env
    :param env:
    :param role:
    :return:
    """
    addrs = _addresses[env]
    if role != 'all':
        ids = addrs[role]
    else:
        ids = []
        for part in _addresses[env].values():
            for host in part:
                if host not in ids:
                    ids.append(host)
    hosts = ['{}'.format(id_) for id_ in ids]
    return hosts


def get_platform_hosts(env, role):
    """
    get instance address of a platform service
    """
    return ['{}'.format(id_)
            for id_ in _platform_addresses[env][role]]

def confirm_env(hosts):
    """
    prompt user to check hosts and user info
    """
    if not confirm('are you sure to operate with the following settings?\n' +
                   'hosts: {}'.format(hosts)):
        abort('abort by user')
