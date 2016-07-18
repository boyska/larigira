import logging
import os
import subprocess

from config import get_conf
log = logging.getLogger('audioscript')


def generate(spec):
    '''
    Recognized arguments (fields in spec):
        - name [mandatory]            script name
        - args [default=empty]   arguments, space-separated
    '''
    conf = get_conf()
    spec.setdefault('args', '')
    args = spec['args'].split()
    for attr in ('name', ):
        if attr not in spec:
            raise ValueError("Malformed audiospec: missing '%s'" % attr)

    scriptpath = os.path.join(conf['SCRIPTS_PATH'], spec['name'])
    if not os.path.exists(scriptpath):
        raise ValueError("Script %s not found", spec['name'])
    if not os.access(scriptpath, os.R_OK | os.X_OK):
        raise ValueError("Insufficient privileges for script %s" % scriptpath)
    if os.stat(scriptpath).st_uid != os.getuid():
        raise ValueError("Script %s owned by %d, should be owned by %d"
                         % (spec['name'], os.stat(scriptpath).st_uid,
                            os.getuid()))
    try:
        log.info('Going to run {}'.format([scriptpath] + args))
        out = subprocess.check_output([scriptpath] + args,
                                      env=dict(
                                          HOME=os.environ['HOME'],
                                          PATH=os.environ['PATH'],
                                          MPD_HOST=conf['MPD_HOST'],
                                          MPD_PORT=str(conf['MPD_PORT'])),
                                      cwd='/')
    except subprocess.CalledProcessError as exc:
        log.error("Error %d when running script %s" %
                  (exc.returncode, spec['name']))
        return []

    out = [p for p in out.split('\n') if p]
    logging.debug('Script %s produced %d files' % (spec['name'], len(out)))
    return out
