from __future__ import print_function
import logging
import gc
from copy import deepcopy

from greenlet import greenlet
from flask import current_app, Blueprint, Flask, jsonify, render_template
from flask_bootstrap import Bootstrap

from .dbadmin import db
from .config import get_conf

rpc = Blueprint('rpc', __name__, url_prefix='/api')
viewui = Blueprint('view', __name__, url_prefix='/view',
                   template_folder='templates')


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
    send_to_parent('refresh')
    return jsonify(dict(status='ok'))


def get_scheduled_audiogen():
    larigira = current_app.larigira
    model = larigira.controller.monitor.model
    running = larigira.controller.monitor.running
    events = {t: {} for t in running.keys()}
    for timespec_eid in events:
        orig_info = running[timespec_eid]
        info = events[timespec_eid]
        info['running_time'] = orig_info['running_time'].isoformat()
        info['audiospec'] = orig_info['audiospec']
        info['timespec'] = model.get_alarm_by_id(timespec_eid)
        if 'actions' in info['timespec']:
            info['timespec']['actions'] = {
                actid: model.get_action_by_id(actid)
                for actid in info['timespec']['actions']}
        info['greenlet'] = hex(id(orig_info['greenlet']))
    return events


@viewui.route('/status/running')
def ui_wip():
    audiogens = get_scheduled_audiogen()
    return render_template('running.html',
                           audiogens=sorted(
                               audiogens.items(),
                               key=lambda x: x[1]['running_time'])
                           )


@rpc.route('/debug/running')
def rpc_wip():
    def treeify(flat):
        roots = [obid for obid in flat if flat[obid]['parent'] not in flat]
        tree = deepcopy(flat)
        for obid in tree:
            tree[obid]['children'] = {}

        to_remove = []
        for obid in tree:
            if obid in roots:
                continue
            if obid not in tree:
                current_app.logger.warn('How strange, {} not in tree'
                                        .format(obid))
                continue
            tree[tree[obid]['parent']]['children'][obid] = tree[obid]
            to_remove.append(obid)

        for obid in to_remove:
            del tree[obid]
        return tree

    greenlets = {}
    for ob in filter(lambda obj: isinstance(obj, greenlet),
                     gc.get_objects()):
        objrepr = {
            'repr': repr(ob),
            'class': ob.__class__.__name__,
        }
        if hasattr(ob, 'parent_greenlet') and ob.parent_greenlet is not None:
            objrepr['parent'] = hex(id(ob.parent_greenlet))
        else:
            objrepr['parent'] = hex(id(ob.parent)) \
                    if ob.parent is not None else None
        if hasattr(ob, 'doc'):
            objrepr['doc'] = ob.doc.split('\n')[0]
        elif ob.__doc__:
            objrepr['doc'] = ob.__doc__.split('\n')[0]

        greenlets[hex(id(ob))] = objrepr

    # TODO: make it a tree

    return jsonify(dict(greenlets=greenlets,
                        greenlets_tree=treeify(greenlets),
                        audiogens=get_scheduled_audiogen(),
                        ))


def create_app(queue, larigira):
    app = Flask('larigira')
    app.config.update(get_conf())
    Bootstrap(app)
    app.register_blueprint(rpc)
    app.register_blueprint(viewui)
    app.register_blueprint(db)
    app.queue = queue
    app.larigira = larigira
    return app
