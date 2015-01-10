#!usr/bin/env python
# -*- coding: utf-8 -*-
"""
job definitions
"""
_jobs = {
    'worker': [
        'worker-resulting',
        'worker-posting',
        'worker-returning',
        'worker-dispatcher',
        'worker-script',
        'resulting-gunicorn',
    ],
    'singleton': [
        'gsm',
        'listener-resulting',
        'admin-gunicorn',
        'merchant-gunicorn',
        'query-balance',
    ],
    'api': [
        'api-gunicorn'
    ]
}


def get_jobs(role):
    """
    returns jobs running on a role
    """
    return _jobs[role]


def get_roles():
    """
    returns all roles defined
    """
    return _jobs.keys()
