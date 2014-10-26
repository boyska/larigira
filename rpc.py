from __future__ import print_function
import logging

from flask import current_app, Blueprint, Flask
rpc = Blueprint('rpc', __name__, url_prefix='/api')


def send_to_parent(kind, *args):
    '''similar to the behaviour of a ParentedLet'''
    if not hasattr(current_app, 'queue'):
        logging.debug('no parent queue; aborting send')
        return
    msg = {
        'emitter': current_app._get_current_object(),
        'class': current_app._get_current_object().__class__.__name__,
        'kind': kind,
        'args': args
    }
    current_app.queue.put(msg)


@rpc.route('/')
def rpc_index():
    return 'So, what command would you like to give?'


@rpc.route('/refresh')
def rpc_refresh():
    send_to_parent('rpc')
    return 'ok, put'


def create_app(queue):
    app = Flask(__name__)
    app.register_blueprint(rpc)
    app.queue = queue
    return app
