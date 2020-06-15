import queue
from multiprocessing import  Queue


class BaseGUI(object):
	def __init__(self):
		self.status_queue = queue.SimpleQueue()
		self.log_queue = Queue(-1)
		self.task_statuses = None
		self.process = None
		self.window_size = (0, 0)
		self.window_status = "Idle"
		self.log = ""
