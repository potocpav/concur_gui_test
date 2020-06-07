import ctypes
import time
import logging
import queue
from threading import activeCount
from threading import current_thread
import concur as c
from src.features.nice_feature.nice_feature import do_work

logger = logging.getLogger('nice-feature')
killed_threads = 0


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


def nice_feature_gui(state, executor):
	thread_pool = list()
	key, value = yield from c.window("Nice Feature", c.orr([
		c.button("Nice Feature"),
		c.button("Close"),
		]))

	if key == "Nice Feature":
		if state.future is None:
			print("Starting computation...")

			for i in range(10):
				state.future = executor.submit(do_work, state.work_id)
				state.future.arg = i
				state.work_id += 1
				thread_pool.append((i, state.future))

			for i, t in reversed(thread_pool):
				executor.submit(terminate_thread, i, t, executor)

		else:
			print("Computation already running.")

	elif key == "Close":
		state.window_visible = False

	return "Modify State", state


def terminate_thread(thread_number, thread, executor):
	global killed_threads
	while True:
		if thread.done():
			try:
				killed_threads += 1
				logger.info(f"killing thread number {thread_number} - {current_thread().ident}. Killed {killed_threads} so far.")
				if killed_threads == 10:
					logger.info(f"Still active threads: {activeCount()}. Attempting to force kill.")
					if activeCount() > 1:
						for t in executor._threads:
							logger.info(f"Killing {t.ident}")
							exc = ctypes.py_object(SystemExit)
							res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(t.ident), exc)
							if res == 0:
								raise ValueError("nonexistent thread id")
							elif res > 1:
								ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
								raise SystemError("PyThreadState_SetAsyncExc failed")
							if activeCount() > 1:
								logger.info(f"Failed. Still active threads: {activeCount()}")
							else:
								logger.info("Success!")

				exc = ctypes.py_object(SystemExit)
				res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(current_thread().ident), exc)
				if res == 0:
					raise ValueError("nonexistent thread id")
				elif res > 1:
					ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
					raise SystemError("PyThreadState_SetAsyncExc failed")
			except Exception as e:
				print(e)
			return
		else:
			logger.info(f"thread {thread} still running.. {activeCount()} total threads active.")
		time.sleep(5)
