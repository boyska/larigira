from __future__ import print_function
import logging
import gc
from greenlet import greenlet

from flask import current_app, Blueprint, Flask, jsonify
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
    rules = list(current_app.url_map.iter_rules())
    return jsonify({'rules': [r.rule for r in rules
                              if r.rule.startswith('/api')]})


@rpc.route('/refresh')
def rpc_refresh():
    send_to_parent('rpc')
    return jsonify(dict(status='ok'))


def get_scheduled_audiogen():
    larigira = current_app.larigira
    model = larigira.monitor.source.model
    running = larigira.monitor.running
    events = {t: {} for t in running.keys()}
    for timespec_eid in events:
        orig_info = running[timespec_eid]
        info = events[timespec_eid]
        info['running_time'] = orig_info['running_time'].isoformat()
        info['audiospec'] = orig_info['audiospec']
        info['timespec'] = model.get_alarm_by_id(timespec_eid)
    return events


@rpc.route('/debug/running')
def rpc_wip():
    greenlets = []
    for ob in filter(lambda obj: isinstance(obj, greenlet),
                     gc.get_objects()):
        greenlets.append({
            'repr': repr(ob),
            'class': ob.__class__.__name__,
            'parent': repr(ob.parent)
        })
    return jsonify(dict(greenlets=greenlets,
                        audiogens=get_scheduled_audiogen(),
                        ))


def create_app(queue, larigira):
    app = Flask(__name__)
    app.register_blueprint(rpc)
    app.queue = queue
    app.larigira = larigira
    return app
