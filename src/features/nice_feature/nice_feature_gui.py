import time
import concur as c
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Process, Queue
import queue
from random import randint


# class NiceFeature:
# 	def __init__(self):
# 		self.do_stuff = True
#
# 	def run(self):
# 		executor = ThreadPoolExecutor(100)
# 		for i in range(10):
# 			executor.submit(self.do_work, randint(1, 10))
# 		executor.shutdown(wait=True)
#
# 	def do_work(self, _input):
# 		if self.do_stuff:
# 			time.sleep(1)
# 			print(_input)


# logger = logging.getLogger('nice-feature')


# class QueueHandler(logging.Handler):
# 	def __init__(self, log_queue):
# 		super().__init__()
# 		self.log_queue = log_queue
#
# 	def emit(self, record):
# 		self.log_queue.put(record)
#

# logging.basicConfig(level=logging.DEBUG)
# log_queue = queue.Queue()
# queue_handler = QueueHandler(log_queue)
# logger.addHandler(queue_handler)

class NiceFeatureState(object):
	def __init__(self, visible):
		self.window_visible = visible
		self.n_threads = 10
		self.n_tasks = 20
		self.status_queue = queue.SimpleQueue()
		self.task_statuses = None
		self.thread = None
		self.status = "Idle"


def nice_thread(q, n_threads, n_tasks):
	def do_work(i, t):
		q.put((i, "Working..."))
		time.sleep(t)
		q.put((i, "Done."))

	# `-1` signifies that the nice_thread status is returned. This is quite ugly. Maybe use two separate queues?
	q.put((-1, "Running..."))
	executor = ThreadPoolExecutor(n_threads)
	for i in range(n_tasks):
		executor.submit(do_work, i, randint(1, 10) / 10)

	executor.shutdown(wait=True)
	q.put((-1, "Work done."))


def thread_table(statuses):
	"""Render a simple table with thread statuses."""
	rows = [c.text_colored("Thread status:", 'yellow')]
	for i, status in enumerate(statuses):
		rows.append(c.text(f"{i:3d}: {status}"))
	return c.orr(rows)


def nice_feature_gui(state, name):
	# use `multi_orr`, so that concurrent events aren't thrown away
	events = yield from c.window(name, c.multi_orr([
		c.tag("Feature Queue", c.listen(state.status_queue)),

		c.slider_int("Number of threads", state.n_threads, 1, 100),
		c.slider_int("Number of tasks", state.n_tasks, 1, 1000),
		c.button("Terminate") if state.thread else c.button("Start"),
		c.button("Close Window"),
		c.separator(),

		c.text_colored("Feature status:", 'yellow'),
		c.text(f"{state.status}"),
		c.separator(),

		c.optional(state.task_statuses, thread_table, state.task_statuses),
		]))

	for tag, value in events:  # This is how event handling works with `multi_orr`
		if tag == "Start":
			assert state.thread is None
			state.status_queue = Queue()
			state.task_statuses = ["Waiting"] * state.n_tasks
			state.thread = Process(target=nice_thread, args=(state.status_queue, state.n_threads, state.n_tasks,))
			state.thread.start()

		elif tag == "Terminate":
			assert state.thread is not None
			state.thread.terminate()
			state.status = "Terminated."
			state.thread = None

		elif tag == "Feature Queue":  # Handle events fired by threads.
			# Update the thread state table
			thread_id, new_status = value
			# Update the feature status
			if thread_id < 0:
				state.status = new_status
				if new_status == "Work done.":
					state.thread = None
			else:
				state.task_statuses[thread_id] = new_status

		elif tag == "Number of tasks":
			state.n_tasks = value

		elif tag == "Number of threads":
			state.n_threads = value

		elif tag == "Close Window":
			state.window_visible = False

	return state
