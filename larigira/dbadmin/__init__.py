'''
This module contains a flask blueprint for db administration stuff

Templates are self-contained in this directory
'''
from __future__ import print_function

from flask import current_app, Blueprint, render_template
db = Blueprint('db', __name__, url_prefix='/db', template_folder='templates')


@db.route('/list')
def db_list():
    model = current_app.larigira.monitor.source.model
    alarms = tuple(model.get_all_alarms())
    events = [(alarm, model.get_actions_by_alarm(alarm))
              for alarm in alarms]
    return render_template('list.html', events=events)
