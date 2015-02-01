from logging import getLogger
log = getLogger('timeform')
from entrypoints_utils import get_one_entrypoint


def get_timeform(kind):
    '''Messes with entrypoints to return a TimeForm'''
    for group in ('larigira.timeform_create', 'larigira.timeform_receive'):
        yield get_one_entrypoint(group, kind)
