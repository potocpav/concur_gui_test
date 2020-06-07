import time
import logging
import queue
from random import randint
from threading import activeCount


logger = logging.getLogger('nice-feature')


class QueueHandler(logging.Handler):
	def __init__(self, log_queue):
		super().__init__()
		self.log_queue = log_queue

	def emit(self, record):
		self.log_queue.put(record)


logging.basicConfig(level=logging.DEBUG)
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)
logger.addHandler(queue_handler)


def do_work(_input):
	sleeping = randint(1, 10)
	logger.info(f"Worker-id {_input} sleeping for {sleeping} seconds.")
	time.sleep(sleeping)

	return _input
