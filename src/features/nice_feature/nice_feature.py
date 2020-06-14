import logging
import queue
from time import sleep
from random import randint


logger = logging.getLogger('nice-feature')


class QueueHandler(logging.Handler):
	def __init__(self, _log_queue):
		super().__init__()
		self.log_queue = _log_queue

	def emit(self, record):
		self.log_queue.put(record)


logging.basicConfig(level=logging.DEBUG)
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)
logger.addHandler(queue_handler)


class NiceFeature:
	def __init__(self, feature_information):
		self.some_information = feature_information
		self.worker_id = None

	def run(self, wid):
		self.worker_id = wid
		sleeptime = randint(1, 10)
		logger.info(f"Worker: {self.worker_id} sleeping for {sleeptime} seconds.")  # TODO: Output this in a log window, that is appended to the feature on the bottom. (See screenshots in the issue)
		sleep(sleeptime)
		return
