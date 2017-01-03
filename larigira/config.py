#!/usr/bin/env python
'''
Taken from flask-appconfig
'''

import json
import os

from xdg import BaseDirectory


def get_conf(prefix='LARIGIRA_'):
    '''This is where everyone should get configuration from'''
    conf_dir = BaseDirectory.save_config_path('larigira')
    conf = {}
    conf['CONTINOUS_AUDIOSPEC'] = dict(kind='mpd', howmany=1)
    conf['MPD_HOST'] = os.getenv('MPD_HOST', 'localhost')
    conf['MPD_PORT'] = int(os.getenv('MPD_PORT', '6600'))
    conf['CACHING_TIME'] = 10
    conf['DB_URI'] = os.path.join(conf_dir, 'db.json')
    conf['SCRIPTS_PATH'] = os.path.join(conf_dir, 'scripts')
    conf['BOOTSTRAP_SERVE_LOCAL'] = True
    conf['SECRET_KEY'] = 'Please replace me!'
    conf['MPD_WAIT_START'] = True
    conf['MPD_WAIT_START_RETRYSECS'] = 5
    conf['CHECK_SECS'] = 20   # period for checking playlist length
    conf['EVENT_TICK_SECS'] = 30  # period for scheduling events
    conf['DEBUG'] = False
    conf['LOG_CONFIG'] = False
    conf['TMPDIR'] = os.getenv('TMPDIR', '/tmp/')
    conf['FILE_PATH_SUGGESTION'] = ()  # tuple of paths
    conf.update(from_envvars(prefix=prefix))
    return conf


def from_envvars(prefix=None, envvars=None, as_json=True):
    """Load environment variables in a dictionary

    Values are parsed as JSON. If parsing fails with a ValueError,
    values are instead used as verbatim strings.

    :param prefix: If ``None`` is passed as envvars, all variables from
                   ``environ`` starting with this prefix are imported. The
                   prefix is stripped upon import.
    :param envvars: A dictionary of mappings of environment-variable-names
                    to Flask configuration names. If a list is passed
                    instead, names are mapped 1:1. If ``None``, see prefix
                    argument.
    :param as_json: If False, values will not be parsed as JSON first.
    """
    conf = {}
    if prefix is None and envvars is None:
        raise RuntimeError('Must either give prefix or envvars argument')

    # if it's a list, convert to dict
    if isinstance(envvars, list):
        envvars = {k: None for k in envvars}

    if not envvars:
        envvars = {k: k[len(prefix):] for k in os.environ.keys()
                   if k.startswith(prefix)}

    for env_name, name in envvars.items():
        if name is None:
            name = env_name

        if env_name not in os.environ:
            continue

        if as_json:
            try:
                conf[name] = json.loads(os.environ[env_name])
            except ValueError:
                conf[name] = os.environ[env_name]
        else:
            conf[name] = os.environ[env_name]

    return conf
