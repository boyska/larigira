import time
import logging
import random
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%H:%M:%S')

from celery import Celery

celery = Celery('hello', backend='redis://localhost',
                broker='redis://localhost:6379/0')


@celery.task(name='create_continous')
def create():
    sec = random.uniform(2, 5)
    time.sleep(sec)
    logging.info('hello world')
    return 'slept! %.2f' % sec

if __name__ == '__main__':
    celery.control.broadcast('pool_restart',
                             arguments={'reload': True})
    res = []
    N = 14

    def callback(*args, **kwargs):
        print(args)
        print(kwargs)
        print('---')

    for i in xrange(N):
        print('append', i)
        res.append(create.apply_async(expires=2))

    for i in xrange(N):
        logging.info('wait %d' % i)
        val = res[i].get()
        logging.info('got %s' % str(val))

    time.sleep(30)
