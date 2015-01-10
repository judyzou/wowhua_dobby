#!/usr/bin/env python
# -*- coding: utf-8 -*-
_config_repos = {
    'live': (
        'wh_live_config', 'http://code.zch168.net/hg_private/wh_live_config/'),
}


def get_config_repo(subnet):
    try:
        return _config_repos[subnet]
    except KeyError:
        raise ValueError(
            'the subnet "{}" does not support the config task'.format(subnet))
