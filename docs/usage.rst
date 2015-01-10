Usage
-----
Help on tasks
`````````````
For a list of available tasks, see::

    $ fab -l

    This file describes common deployment tasks for ticket center.

    Available commands:

        current      show current version of ticket center
        hosts        connect to the specified hosts.
        script       Run a script in `live_scripts/bin`.
        update       update `live_scripts`; update ticket center and install new ...
        upstart      operate on all upstart jobs defined for a role of hosts.
        upstart_job  operate on a given upstart job. The role of the hosts is imp...

To get help on a specific task::

    $ fab -d update
    Displaying detailed information for task 'update':

        update `live_scripts`; update ticket center and install new packages

        :param str rev: hg revision of ticket center to be updated to

        Arguments: rev

Run a task
``````````
First example::

    # check what version of ticket center the API machines in Beta are running
    $ fab -u a10071 hosts:beta,api current

The `-u` option specifies the user with which to login the remote machine. If
you're using SSH keys, you're on automatically; otherwise, you'll be prompted
for login password. Optionally, you can set login password with the `-p`
option::

    $ fab -u a10071 -p 123456 hosts:beta,api current

Normally, the `hosts` task would ask for your confirmation before proceeding.
You can suppress it by giving it a 3rd parameter "Y"::

    $ fab -u a10071 -p 123456 hosts:beta,api,Y current

With `-p`, `-u` and `Y` all set, most of the tasks can be performed without
human intervention. You can execute tasks in parallel now by supplying the `-P`
option::

    $ fab -u a10071 -p 123456 -P hosts:beta,all,Y update:ef7a9eabc934

The above task updates code/dependencies on all beta machines in parallel.

More examples
`````````````
::

    # check the state of the worker processes
    $ fab hosts:beta,worker upstart:status

    # restart services on singleton
    $ fab hosts:beta,singleton upstart:restart

    # run a script in live_script/bin
    $ fab hosts:beta,singleton script:resend_job.py,"1102123 10.1.7.240:11300"

For more advanced usages, see `Fabric`_.

.. seealso:: tasks are defined here: :mod:`~dobby.fabfile`

Usage Patterns
``````````````
* Update without DB schema change::

    # 1. update code, install dependency and apply production config
    fab -u root -p 123 -P hosts:beta,all,Y update:ef7a9eabc934 config

    # 2. restart services
    fab -u root -p 123 -P hosts:beta,singleton,Y upstart:restart
    fab -u root -p 123 -P hosts:beta,worker,Y upstart:restart
    fab -u root -p 123 -P hosts:beta,api,Y upstart:restart

* Update with DB schema change::

    # 1. update code, install dependency and apply production config
    fab -u root -p 123 -P hosts:beta,all,Y update:ef7a9eabc934 config

    # 2. stop services
    fab -u root -p 123 -P hosts:beta,singleton,Y upstart:stop
    fab -u root -p 123 -P hosts:beta,worker,Y upstart:stop
    fab -u root -p 123 -P hosts:beta,api,Y upstart:stop

    # 3. update db schema
    # psql ...

    # 4. start services
    fab -u root -p 123 -P hosts:beta,singleton,Y upstart:start
    fab -u root -p 123 -P hosts:beta,worker,Y upstart:start
    fab -u root -p 123 -P hosts:beta,api,Y upstart:start




.. _`Fabric`: http://www.fabfile.org/
