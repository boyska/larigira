'''
This module is for the main application logic
'''
from __future__ import print_function
from gevent import monkey
monkey.patch_all(subprocess=True)

import sys
import os
import tempfile
import signal
from time import sleep
import logging
FORMAT = '%(asctime)s|%(levelname)s[%(name)s:%(lineno)d] %(message)s'
logging.basicConfig(level=logging.INFO,
                    format=FORMAT,
                    datefmt='%H:%M:%S')

import gevent
from gevent.wsgi import WSGIServer

from .mpc import Controller, get_mpd_client
from .event import Monitor
from .config import get_conf
from .rpc import create_app


def on_main_crash(*args, **kwargs):
    print('A crash occurred in "main" greenlet. Aborting...')
    sys.exit(1)


class Larigira(object):
    def __init__(self):
        self.log = logging.getLogger('larigira')
        self.conf = get_conf()
        self.controller = Controller(self.conf)
        if 'DB_URI' in self.conf:
            self.monitor = Monitor(self.controller.q, self.conf)
        else:
            self.monitor = None
        self.controller.link_exception(on_main_crash)
        self.http_server = WSGIServer(('', 5000),
                                      create_app(self.controller.q, self))

    def start(self):
        self.controller.start()
        if self.monitor is not None:
            self.monitor.start()
        self.http_server.start()


def main():
    os.environ['TMPDIR'] = tempfile.mkdtemp(prefix='larigira')
    logging.basicConfig(level=logging.DEBUG)
    if(get_conf()['MPD_WAIT_START']):
        while True:
            try:
                get_mpd_client(get_conf())
            except Exception:
                logging.debug("Could not connect to MPD, waiting")
                sleep(int(get_conf()['MPD_WAIT_START_RETRYSECS']))
            else:
                logging.info("MPD ready!")
                break



    larigira = Larigira()
    larigira.start()

    def sig(*args):
        print('invoked sig', args)
        larigira.controller.q.put(dict(kind='signal', args=args))
    gevent.signal(signal.SIGHUP, sig, signal.SIGHUP)
    gevent.wait()

if __name__ == '__main__':
    main()
