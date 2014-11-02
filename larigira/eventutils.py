import gevent


class ParentedLet(gevent.Greenlet):
    '''
    ParentedLet is just a helper subclass that will help you when your
    greenlet main duty is to "signal" things to a parent_queue.

    It won't save you much code, but "standardize" messages and make explicit
    the role of that greenlet
    '''
    def __init__(self, queue):
        gevent.Greenlet.__init__(self)
        self.parent_queue = queue
        self.tracker = None  # set this to recognize easily

    def parent_msg(self, kind, *args):
        return {
            'emitter': self,
            'class': self.__class__.__name__,
            'tracker': self.tracker,
            'kind': kind,
            'args': args
        }

    def send_to_parent(self, kind, *args):
        self.parent_queue.put(self.parent_msg(kind, *args))

    def _run(self):
        if not hasattr(self, 'do_business'):
            raise Exception("do_business method not implemented by %s" %
                            self.__class__.__name__)
        for msg in self.do_business():
            self.send_to_parent(*msg)


class CeleryTask(ParentedLet):
    def __init__(self, task, queue, task_args=tuple(), **kwargs):
        ParentedLet.__init__(self, queue)
        self.task = task
        self.task_args = task_args
        self.apply_async_args = kwargs

    def parent_msg(self, kind, *args):
        msg = ParentedLet.parent_msg(self, kind, *args)
        msg['task'] = self.task
        return msg

    def do_business(self):
        asyncres = self.task.apply_async(self.task_args,
                                         **self.apply_async_args)
        val = asyncres.get()
        yield ('celery', val)


class Timer(ParentedLet):
    def __init__(self, milliseconds, queue):
        ParentedLet.__init__(self, queue)
        self.ms = milliseconds

    def parent_msg(self, kind, *args):
        msg = ParentedLet.parent_msg(self, kind, *args)
        msg['period'] = self.ms
        return msg

    def do_business(self):
        while True:
            gevent.sleep(self.ms / 1000.0)
            yield ('timer', )
