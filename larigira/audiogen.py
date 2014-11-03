from __future__ import print_function
import sys
import argparse
from pkg_resources import iter_entry_points
import json
import logging


def get_audiogenerator(kind):
    '''Messes with entrypoints to return an audiogenerator function'''
    points = tuple(iter_entry_points(group='larigira.audiogenerators',
                                     name=kind))
    if not points:
        raise ValueError('cant find a generator for ', kind)
    if len(points) > 1:
        logging.warning("Found more than one audiogenerator for '%s'" % kind)
    gen = points[0]
    return gen.load()


def get_parser():
    parser = argparse.ArgumentParser(
        description='Generate audio and output paths')
    parser.add_argument('audiospec', metavar='AUDIOSPEC', type=str, nargs=1,
                        help='filename for audiospec, formatted in json')
    return parser


def read_spec(fname):
    if fname == '-':
        return json.load(sys.stdin)
    with open(fname) as buf:
        return json.load(buf)


def check_spec(spec):
    if 'kind' not in spec:
        yield "Missing field 'kind'"


def audiogenerate(spec):
    gen = get_audiogenerator(spec['kind'])
    return tuple(gen(spec))


def main():
    '''Main function for the "larigira-audiogen" executable'''
    args = get_parser().parse_args()
    spec = read_spec(args.audiospec[0])
    errors = tuple(check_spec(spec))
    if errors:
        logging.error("Errors in audiospec")
        for err in errors:
            print(err)  # TODO: to stderr
        sys.exit(1)
    for path in audiogenerate(spec):
        print(path)


if __name__ == '__main__':
    main()
