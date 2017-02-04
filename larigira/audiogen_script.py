'''
script audiogenerator: uses an external program to generate audio URIs

a script can be any valid executable in
$XDG_CONFIG_DIR/larigira/scripts/<name>; for security reasons, it must be
executable and owned by the current user. The audiospec can specify arguments
to the script, while the environment cannot be customized (again, this is for
security reasons).

The script should assume a minimal environment, and being run from /.  It must
output one URI per line; please remember that URI must be understood from mpd,
so file paths are not valid; file:///file/path.ogg is a valid URI instead.
The output MUST be UTF-8-encoded.
Empty lines will be skipped.  stderr will be logged, so please be careful.  any
non-zero exit code will result in no files being added.and an exception being
logged.
'''
import logging
import os
import subprocess

from .config import get_conf
log = logging.getLogger(__name__)


def generate(spec):
    '''
    Recognized arguments (fields in spec):
        - name [mandatory]            script name
        - args [default=empty]   arguments, colon-separated
    '''
    conf = get_conf()
    spec.setdefault('args', '')
    if type(spec['args']) is str:
        args = spec['args'].split(';')
    args = list(spec['args'])
    for attr in ('name', ):
        if attr not in spec:
            raise ValueError("Malformed audiospec: missing '%s'" % attr)

    if '/' in spec['name']:
        raise ValueError("Script name is a filename, not a path ({} provided)"
                         .format(spec['name']))
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
        log.info('Going to run %s', [scriptpath] + args)
        env = dict(
            HOME=os.environ['HOME'],
            PATH=os.environ['PATH'],
            MPD_HOST=conf['MPD_HOST'],
            MPD_PORT=str(conf['MPD_PORT'])
        )
        if 'TMPDIR' in os.environ:
            env['TMPDIR'] = os.environ['TMPDIR']
        out = subprocess.check_output([scriptpath] + args,
                                      env=env,
                                      cwd='/')
    except subprocess.CalledProcessError as exc:
        log.error("Error %d when running script %s",
                  exc.returncode, spec['name'])
        return []

    out = out.decode('utf-8')
    out = [p for p in out.split('\n') if p]
    logging.debug('Script %s produced %d files', spec['name'], len(out))
    return out
generate.description = 'Generate audio through an external script. ' \
'Experts only.'
