from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Queue
import concur as c
import imgui


class BaseGUI(object):
	def __init__(self):
		self.base = None
		self.status_queue = Queue()
		self.log_queue = Queue(-1)
		self.task_statuses = None
		self.process = None
		self.window_size = (0, 0)
		self.window_status = "Idle"
		self.n_threads = 500
		self.n_tasks = 1
		self.information_dict = None
		self.log = ""
		self.username = ""
		self.password = ""

	def threadify(self, _feature, information_dict: dict):
		# `-1` signifies that the nice_thread status is returned. This is quite ugly. Maybe use two separate queues?
		feature = _feature(information_dict)
		self.status_queue.put((-1, "Running..."))

		executor = ThreadPoolExecutor(self.n_threads)
		for i in range(self.n_tasks):
			executor.submit(self.append_to_queue, wid=i, feature=feature)
		executor.shutdown(wait=True)
		self.status_queue.put((-1, "Work done."))

	def append_to_queue(self, wid: int, feature):
		self.status_queue.put((wid, "Working..."))
		assert hasattr(feature, "run") and callable(feature.run) is True
		feature.run()
		self.status_queue.put((wid, "Done."))

	def generate_thread_table(self):
		"""Render a simple table with thread statuses."""
		rows = [c.text_colored("Thread status:", 'yellow')]
		if self.task_statuses:
			for i, status in enumerate(self.task_statuses):
				rows.append(c.text(f"{i}: {status}"))
			return c.collapsing_header("Thread status", c.optional(bool(self.task_statuses), c.orr, rows), open=False)

	@staticmethod
	def validating_button(label, error, tag=None):
		""" Validating button.
		Behaves in the same way as a regular `concur.widgets.button` when `error` is None.
		When `error` is a string, it displays an error popup instead of emitting an event.
		"""
		while True:
			if imgui.button(label):
				if error is not None:
					imgui.open_popup("Error Popup")
				else:
					return tag if tag is not None else label, None

			if imgui.begin_popup("Error Popup"):
				imgui.text(error)
				if imgui.button("OK"):
					imgui.close_current_popup()
					imgui.end_popup()
					return tag if tag is not None else label, None
				imgui.same_line()
				if imgui.button("Cancel"):
					imgui.close_current_popup()
				imgui.end_popup()
			yield

	# These two widgets are not in Concur, so they show how to add new widgets.
	@staticmethod
	def log_widget(text):
		""" Log widget with auto-scroll. """
		while True:
			# https://pyimgui.readthedocs.io/en/latest/reference/imgui.core.html#imgui.core.push_text_wrap_position
			imgui.push_text_wrap_pos()
			imgui.text_unformatted(text)
			imgui.pop_text_wrap_pos()
			if imgui.get_scroll_y() >= imgui.get_scroll_max_y():
				imgui.set_scroll_here(1.0)
			yield

	def render(self):
		pass
