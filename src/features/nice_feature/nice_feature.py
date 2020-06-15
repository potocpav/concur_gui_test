import logging.handlers
from time import sleep
from random import randint
# from multiprocessing import Queue


class NiceFeature:
	def __init__(self, feature_information, log_queue):
		self.logger = logging.getLogger('nice-feature')
		logging.basicConfig(level=logging.DEBUG)
		queue_handler = logging.handlers.QueueHandler(log_queue)
		self.logger.addHandler(queue_handler)

		self.some_information = feature_information
		self.worker_id = None

	def run(self, wid):
		self.worker_id = wid
		sleeptime = randint(1, 10)
		self.logger.info(f"Worker: {self.worker_id} sleeping for {sleeptime} seconds.")  # TODO: Output this in a log window, that is appended to the feature on the bottom. (See screenshots in the issue)
		sleep(sleeptime)
		return
