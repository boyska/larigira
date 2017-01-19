from logging import getLogger
log = getLogger('entrypoints_utils')
from pkg_resources import iter_entry_points


def get_one_entrypoint(group, kind):
    '''Messes with entrypoints to return an entrypoint of a given group/kind'''
    points = tuple(iter_entry_points(group=group, name=kind))
    if not points:
        raise ValueError('cant find an entrypoint %s:%s' % (group, kind))
    if len(points) > 1:
        log.warning("Found more than one timeform for %s:%s", group, kind)
    return points[0].load()


def get_avail_entrypoints(group):
    return [e.name for e in iter_entry_points(group=group)]
