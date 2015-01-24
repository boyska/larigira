from __future__ import print_function
import argparse
from pprint import pprint

from .event import EventModel


def main_list(args):
    m = EventModel(args.file)
    for alarm, action in m.get_all_alarms_expanded():
        pprint(dict(alarm=alarm, action=action), indent=4)


def main_add(args):
    m = EventModel(args.file)
    m.add_event(dict(kind='frequency', interval=args.interval, start=1),
                [dict(kind='mpd', howmany=1)]
                )


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-f', '--file', help="Filepath for DB", required=True)
    sub = p.add_subparsers()
    sub_list = sub.add_parser('list')
    sub_list.set_defaults(func=main_list)
    sub_add = sub.add_parser('add')
    sub_add.add_argument('--interval', type=int, default=3600)
    sub_add.set_defaults(func=main_add)

    args = p.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
