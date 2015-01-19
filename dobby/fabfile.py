"""
This file describes common deployment tasks for ticket center.
"""
import os
from fabric.api import run, cd
from fabric.context_managers import settings
from fabric.contrib.console import confirm
from fabric.operations import sudo, put
from fabric.state import env
from fabric.utils import abort
from dobby.config import get_config_repo
from dobby.hosts import get_hosts, confirm_env, get_platform_hosts
from dobby.jobs import get_jobs
from dobby.utils import zch, zchenv, VIRTUALENV


__all__ = [
    'hosts', 'setup_zch', 'init_code', 'update_code', 'install_upstarts',
    'current', 'update', 'config', 'upstart', 'upstart_job', 'script',
    'munin_plugin', 'platform', 'cron',
]


CRON_PATH = '/etc/cron.d'

from fabric.api import run

def hosts(subnet, role, confirmed=None):
    """
    connect to the ticket center application services hosts.

    :param subnet:
        the subnet to connect, one of `('alpha', 'beta', 'live', 'all')`
    :param role:
        the role of hosts to connect, one of `('api', 'admin', 'cron')`
    """
    _hosts = get_hosts(subnet, role)
    if confirmed != 'Y':
        confirm_env(_hosts)
    env.hosts = _hosts
    env.zch_role = role
    env.zch_subnet = subnet


def platform(subnet, role, confirmed=None):
    """
    connect to platform services hosts

    :param subnet:
    :param role:
    :return:
    """
    _hosts = get_platform_hosts(subnet, role)
    if confirmed != 'Y':
        confirm_env(_hosts)
    env.hosts = _hosts
    env.zch_role = role
    env.zch_subnet = subnet


def setup_zch():
    with settings(warn_only=True):
        if sudo('test -d /zch').failed:
            put('./provision.sh', '/home/leopold')
            sudo('bash provision.sh')
            sudo("echo '%sudo   ALL=(zch) NOPASSWD: /bin/bash' >> /etc/sudoers")
            with zch():
                sudo('mkdir -p /zch/virtualenvs /zch/src /zch/.ssh')
                sudo('virtualenv /zch/virtualenvs/zchenv')
            put('./deploy_keys/wowhua', '/zch/.ssh', use_sudo=True, mode=0600)
            put('./deploy_keys/ssh_config', '/zch/.ssh/config', use_sudo=True, mode=0600)
            sudo('chown zch.zch /zch/.ssh/wowhua')
            sudo('chown zch.zch /zch/.ssh/config')

            put('./cron/ntp_time', '/etc/cron.daily/', use_sudo=True, mode=0700)
            sudo('chown root.root /etc/cron.daily/ntp_time')


def update(rev):
    """
    update `live_scripts`; update ticket center and install new packages

    :param str rev: hg revision of ticket center to be updated to
    """
    with zch():
        with cd('/zch/src/wowhua_box'):
            sudo('hg pull')
            sudo('hg update -r {}'.format(rev))
            with zchenv():
                sudo('pip install -r requirements.txt')
        with cd('/zch/live_scripts'):
            sudo('hg pull -u')


def current():
    """
    show current version of ticket center
    """
    with zch():
        with cd('/zch/src/wowhua_box'):
            sudo('hg summary')
            sudo('whoami')


def upstart_job(action, job):
    """
    operate on a given upstart job. The role of the hosts is implicitly set in
    the previous `hosts` task. This task does not support the "all" role.

    :param action:
        one of 'start', 'status', 'stop', 'restart', 'link'. The 'link' command
        links a upstart conf in `live_scripts` to `/etc/init`.
    :param job: name of the job
    """
    if action not in ('start', 'status', 'stop', 'restart', 'link'):
        abort('undefined upstart action: {}'.format(action))
    if action != 'link':
        sudo('{} {}'.format(action, job))
    else:
        link = 'ln -s /zch/live_scripts/upstart/{}.conf'.format(job)
        with settings(warn_only=True):
            with cd('/etc/init'):
                r = sudo(link)
                if r.failed:
                    if confirm('job already exists; Replace?'):
                        sudo('rm {}.conf'.format(job))
                        sudo(link)
                    else:
                        abort('abort link')
                sudo('initctl reload-configuration')


def upstart(action):
    """
    operate on all upstart jobs defined for a role of hosts.
    The role of the VM is implicitly set in the previous `hosts` task.
    This task does not support the "all" role.

    :param action: one of 'start', 'status', 'stop', 'restart'
    """
    if action not in ('start', 'status', 'stop', 'restart'):
        abort('undefined upstart action: {}'.format(action))
    if env.zch_role == 'all':
        abort('the task "upstart" cannot be executed on all roles.'
              ' Choose one at a time')
    for job in get_jobs(env.zch_role):
        upstart_job(action, job)


def install_upstarts():
    for job in ['api-gunicorn', 'admin-gunicorn']:
        upstart_job('link', job)


ALLOWED_SCRIPT_TYPES = {
    'py': 'python',
    'sh': 'bash'
}


def script(name, args=None, ext=None):
    """
    Run a script in `live_scripts/bin`.

    :param str name:
        name of the script to run, including extension. E.g.,
        `query_balance.py`. Python scripts are run in zchenv.
    :param str args: args for the script.
    :param str ext: script type, one of `sh` or `py`
    """
    if not ext:
        ext = name.split('.')[-1]
        if not ext:
            abort(
                'interpreter not set and it cannot be determined ' +
                'from "{}"'.format(name)
            )
    try:
        interpreter = ALLOWED_SCRIPT_TYPES[ext]
    except KeyError:
        abort('No interpreter configured for the type "{}"'.format(ext))
    else:
        if args:
            cmd = '{} {}'.format(name, args)
        else:
            cmd = name
        with cd('/zch/live_scripts/bin'):
            with zch():
                if interpreter == 'python':
                    with zchenv():
                        sudo('python {}'.format(cmd))
                elif interpreter == 'bash':
                    sudo('bash {}'.format(cmd))

def init_code():
    with zch():
        with settings(warn_only=True):
            if sudo('test -d /zch/src/wowhua_box').failed:
                sudo('hg clone ssh://hg@bitbucket.org/lingxiaoinc/wowhua_box/ ' +
                     '/zch/src/wowhua_box')
            if sudo('test -d /zch/live_scripts').failed:
                sudo('ln -s /zch/src/wowhua_box/live_scripts /zch/live_scripts')
        with cd('/zch/src/wowhua_box'):
            with zchenv():
                sudo('pip install -r requirements.txt')
    config()

def update_code():
    """
    update source
    """
    with zch():
        with cd('/zch/src/wowhua_box'):
            sudo('hg pull -u')


def munin_plugin(*plugin_name):
    """
    install python munin plugins. They are run in `zchenv` when invoked
    """
    for name in plugin_name:
        py = '/zch/live_scripts/munin_plugins/{}.py'.format(name)
        sudo('test -e {}'.format(py))
        plugin = '{}/bin/python {} $1'.format(VIRTUALENV, py)
        with cd('/etc/munin/plugins'):
            sudo("echo '{}' > {}".format(plugin, name))
            sudo('chmod a+x {}'.format(name))
    sudo('service munin-node restart')


def config():
    """
    install production configuration in service's ".d" directory
    """
    with zch():
        config_dir = '/zch/live_scripts/etc/{}/'.format(env.zch_subnet)
        with zchenv():
            sudo('/zch/live_scripts/bin/link_config.py {}'.format(config_dir))


def cron(name, state='present'):
    """
    install a cron job

    :param name: name to identify the cron job
    :param state: one of 'present' or 'absent'
    """
    tab_path = os.path.join(CRON_PATH, name)
    if state == 'absent':
        sudo('rm -f {}'.format(tab_path))
    elif state == 'present':
        sudo('cp /zch/live_scripts/cron/{} {}'.format(name, tab_path))
    else:
        abort('state can only be "present" or "absent"')
