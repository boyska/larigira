'''
This module is for the main application logic
'''
from __future__ import print_function
from gevent import monkey
monkey.patch_all(subprocess=True)

import sys
import signal
import logging
FORMAT = '%(asctime)s|%(levelname)s[%(name)s:%(lineno)d] %(message)s'
logging.basicConfig(level=logging.INFO,
                    format=FORMAT,
                    datefmt='%H:%M:%S')

import gevent
from gevent.wsgi import WSGIServer

from .mpc import Player
from .event import Monitor
from .config import get_conf
from .rpc import create_app


def on_player_crash(*args, **kwargs):
    print('A crash occurred in "main" greenlet. Aborting...')
    sys.exit(1)


class Larigira(object):
    def __init__(self):
        self.log = logging.getLogger('larigira')
        self.conf = get_conf()
        self.player = Player(self.conf)
        if 'DB_URI' in self.conf:
            self.monitor = Monitor(self.player.q, self.conf)
        else:
            self.monitor = None
        self.player.link_exception(on_player_crash)
        self.http_server = WSGIServer(('', 5000),
                                      create_app(self.player.q, self))

    def start(self):
        self.player.start()
        if self.monitor is not None:
            self.monitor.start()
        self.http_server.start()


def main():
    logging.basicConfig(level=logging.DEBUG)
    larigira = Larigira()
    larigira.start()

    def sig(*args):
        print('invoked sig', args)
        larigira.player.q.put('signal', *args)
    gevent.signal(signal.SIGHUP, sig, signal.SIGHUP)
    gevent.wait()

if __name__ == '__main__':
    main()
