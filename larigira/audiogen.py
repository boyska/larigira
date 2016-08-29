from __future__ import print_function
import sys
import argparse
from .entrypoints_utils import get_one_entrypoint
import json
from logging import getLogger
log = getLogger('audiogen')


def get_audiogenerator(kind):
    '''Messes with entrypoints to return an audiogenerator function'''
    return get_one_entrypoint('larigira.audiogenerators', kind)


def get_parser():
    parser = argparse.ArgumentParser(
        description='Generate audio and output paths')
    parser.add_argument('audiospec', metavar='AUDIOSPEC', type=str, nargs=1,
                        help='filename for audiospec, formatted in json')
    return parser


def read_spec(fname):
    try:
        if fname == '-':
            return json.load(sys.stdin)
        with open(fname) as buf:
            return json.load(buf)
    except ValueError:
        sys.stderr.write("Error: invalid JSON\n")
        sys.exit(1)


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
        log.error("Errors in audiospec")
        for err in errors:
            sys.stderr.write('Error: {}\n'.format(err))
        sys.exit(1)
    for path in audiogenerate(spec):
        print(path)


if __name__ == '__main__':
    main()
