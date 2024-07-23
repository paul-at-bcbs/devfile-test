import logging
import asyncio
import aiohttp
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
import time
import requests
from atexit import register
import json
import logging.config

import foo

## load config file - if not there then proceed silently
## reset logging to wipe out everything
## set up new log with HTTP
## send log entry that logging has completed its set up and ready to be used.
## make it a single file; add the file to cli (will have to copy to all python ones.)
## make dir, __init__.py with all methods but try with just a single file.
## handle log hierarchy with async.xxxx where all must start with async to get it.


'''
    hcsclogging
        .reset(True)
        .fromConfig(True)
        .useEnv(True)
        .addToRoot(True)
        .initialize()

    hcsclogging.config({
        "rest": True,
        "fromConfig": True,
    
    }).initialize()

'''



class SyncHTTPHandler(logging.Handler):
    def __init__(self, url, method='POST'):
        super().__init__()
        self.url = url
        self.method = method
        
    def send_log(self, log_entry):
        headers = {'Content-Type': 'application/json'}
        payload = {
                'name': 'app01',
                'name': log_entry,
                'time': 'Monday'
            }

        print("SEnding logs!!!!")
        
        if self.method.upper() == 'POST':
            response = requests.post(self.url, json=payload, headers=headers)
            print(response)
        elif self.method.upper() == 'PUT':
            response = requests.put(self.url, json=payload, headers=headers)
            print(response)
        else:
            raise ValueError(f"Unsupported method: {self.method}")

    def emit(self, record):
        log_entry = self.format(record)
        #time.sleep(2)
        self.send_log(log_entry)

# reset logging in case other were messing with it
def reset_logging():
    manager = logging.root.manager
    manager.disabled = logging.NOTSET
    for logger in manager.loggerDict.values():
        if isinstance(logger, logging.Logger):
            logger.setLevel(logging.NOTSET)
            logger.propagate = True
            logger.disabled = False
            logger.filters.clear()
            handlers = logger.handlers.copy()
            for handler in handlers:
                # Copied from `logging.shutdown`.
                try:
                    handler.acquire()
                    handler.flush()
                    handler.close()
                except (OSError, ValueError):
                    pass
                finally:
                    handler.release()
                logger.removeHandler(handler)


# Setup logging
def setup_logging():
    queue = Queue()
    queue_handler = QueueHandler(queue)
    queue_listener = QueueListener(queue, SyncHTTPHandler('http://localhost:8000/items/123'))

    logger = logging.getLogger('async_logger')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(queue_handler)
    logger.propagate = False
    queue_listener.start()
    register(queue_listener.stop)

    #logging.getLogger().addHandler(queue_handler)
    return logger

# Sample usage
if __name__ == "__main__":
    
    reset_logging()
    # set up logging via config
    with open('logging-config.json', 'r') as f:
        config = json.load(f)
    logging.config.dictConfig(config)

    default_logger = logging.getLogger()

    # inject HTTP logger
    named_logger1 = setup_logging()
    named_logger = logging.getLogger('async_logger.foo2')

    root_logger = logging.getLogger()


    root_logger.debug('This is a debug message')
    root_logger.info('This is an info message')
    root_logger.warning('This is a warning message')
    root_logger.error('This is an error message')
    named_logger.critical('This is a critical message')
   
    foo.foo()
    time.sleep(15)
