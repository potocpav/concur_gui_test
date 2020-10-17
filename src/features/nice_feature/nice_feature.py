import logging.handlers
from random import randint
from time import sleep


class NiceFeature:
	def __init__(self, information_dict):
		self.logger = logging.getLogger('nice-feature')
		logging.basicConfig(level=logging.DEBUG)
		queue_handler = logging.handlers.QueueHandler(information_dict['log_queue'])
		self.logger.addHandler(queue_handler)

		self.some_information = information_dict['information']
		self.worker_id = None

	def run(self):
		sleeptime = randint(1, 10)

		# TODO The smiley is displayed as ? in the log widget
		self.logger.info(f"A worker is sleeping for {sleeptime} seconds 😄.|green")

		# As Omar says (googled "imgui termial colors text widget"), you have to roll out your own colored-text widget.
		# https://twitter.com/ocornut/status/972421631443337216?lang=en
		#
		# If all you need is per-line colors, it should be very easy. Just create `c.text_colored` widgets, one per each line.
		#
		# self.logger.info(colored.stylize(f"Worker: {self.worker_id} sleeping for {sleeptime} seconds.", self.good))
		sleep(sleeptime)
		return
