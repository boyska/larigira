'''
main module to read and get informations about alarms
'''
from __future__ import print_function
import sys
import argparse
from pkg_resources import iter_entry_points
import json
import logging
from datetime import datetime


def get_timegenerator(kind):
    '''Messes with entrypoints to return an timegenerator function'''
    points = tuple(iter_entry_points(group='larigira.timegenerators',
                                     name=kind))
    if not points:
        raise ValueError('cant find a generator for ', kind)
    if len(points) > 1:
        logging.warning("Found more than one timegenerator for '%s'" % kind)
    gen = points[0]
    return gen.load()


def get_parser():
    parser = argparse.ArgumentParser(
        description='Generate "ring times" from a timespec')
    parser.add_argument('timespec', metavar='TIMESPEC', type=str, nargs=1,
                        help='filename for timespec, formatted in json')
    parser.add_argument('--now', metavar='NOW', type=int, nargs=1,
                        default=None,
                        help='Set a different "time", in unix epoch')
    parser.add_argument('--howmany', metavar='N', type=int, nargs=1,
                        default=[1],
                        help='Set a different "time", in unix epoch')
    return parser


def read_spec(fname):
    if fname == '-':
        return json.load(sys.stdin)
    with open(fname) as buf:
        return json.load(buf)


def check_spec(spec):
    if 'kind' not in spec:
        yield "Missing field 'kind'"


def timegenerate(spec, now=None, howmany=1):
    Alarm = get_timegenerator(spec['kind'])
    generator = Alarm(spec)
    if now is not None:
        if type(now) is not datetime:
            now = datetime.fromtimestamp(now)
    for _ in xrange(howmany):
        now = generator.next_ring(current_time=now)
        yield now


def main():
    '''Main function for the "larigira-timegen" executable'''
    args = get_parser().parse_args()
    spec = read_spec(args.timespec[0])
    errors = tuple(check_spec(spec))
    if errors:
        logging.error("Errors in timespec")
        for err in errors:
            print(err)  # TODO: to stderr
        sys.exit(1)
    now = None if args.now is None else args.now.pop()
    howmany = None if args.howmany is None else args.howmany.pop()
    for time in timegenerate(spec, now=now, howmany=howmany):
        print(time)
