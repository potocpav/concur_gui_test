import time
from concurrent.futures.thread import ThreadPoolExecutor
from random import randint


class NiceFeature:
	def __init__(self):
		self.do_stuff = True

	def run(self):
		executor = ThreadPoolExecutor(100)
		for i in range(10):
			executor.submit(self.do_work, randint(1, 10))
		print("Waiting")
		executor.shutdown(wait=True)
		print("Done.")

	def do_work(self, _input):
		if self.do_stuff:
			time.sleep(1)
			print(_input)
