import concur as c
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Process, Queue
import imgui
from src.features.base.BaseGUI import BaseGUI
from src.features.nice_feature.nice_feature import NiceFeature


class NiceFeatureGUI(BaseGUI):

	def __init__(self):
		super().__init__()

		self.name = "Nice Feature"
		self.n_threads = 10
		self.n_tasks = 20
		self.information = ""

	def threadify(self):
		nice_feature = NiceFeature(feature_information=self.information, log_queue=self.log_queue)
		# `-1` signifies that the nice_thread status is returned. This is quite ugly. Maybe use two separate queues?
		self.status_queue.put((-1, "Running..."))

		executor = ThreadPoolExecutor(self.n_threads)
		for i in range(self.n_tasks):
			executor.submit(self.append_to_queue, wid=i, feature_object=nice_feature)
		executor.shutdown(wait=True)
		self.status_queue.put((-1, "Work done."))

	# wid = worker id
	def append_to_queue(self, wid: int, feature_object: NiceFeature):
		self.status_queue.put((wid, "Working..."))
		feature_object.run(wid)
		self.status_queue.put((wid, "Done."))

	def generate_thread_table(self):
		"""Render a simple table with thread statuses."""
		rows = [c.text_colored("Thread status:", 'yellow')]
		if self.task_statuses:
			for i, status in enumerate(self.task_statuses):
				rows.append(c.text(f"{i}: {status}"))
			return c.collapsing_header("Thread status", c.optional(bool(self.task_statuses), c.orr, rows), open=False)

	# These two widgets are not in Concur, so they show how to add new widgets.
	@staticmethod
	def log_widget(text):
		""" Log widget with auto-scroll. """
		while True:
			imgui.text_unformatted(text)
			if imgui.get_scroll_y() >= imgui.get_scroll_max_y():
				imgui.set_scroll_here(1.0)
			yield

	@staticmethod
	def validating_button(label, error, tag=None):
		""" Validating button.
		Behaves in the same way as a regular `concur.widgets.button` when `error` is None.
		When `error` is a string, it displays an error popup instead of emitting an event.
		TODO: Popup functionality
		This kind of popup I would call a blocking popup which prevents the user from starting the feature.
		How could I make it, that the user will see a popup which is just a warning or information but he can still proceeed to start the feature?
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
			yield

	def render(self):
		# use `multi_orr`, so that concurrent events aren't thrown away
		events = yield from	c.window(self.name, c.multi_orr([
			c.tag(tag_name="Status Queue", elem=c.listen(self.status_queue)),
			c.tag("Log Queue", c.listen(self.log_queue)),

			c.slider_int("Number of threads", self.n_threads, 1, 100),
			c.slider_int("Number of tasks", self.n_tasks, 1, 1000),
			c.input_text(name="Information, the feature needs", value=self.information, tag="Information"),
			c.button("Terminate") if self.process
			else self.validating_button("Start",
			None if self.information
			else "Feature information is missing!"),
			c.separator(),

			c.text_colored("Feature status:", 'yellow'),
			c.text(f"{self.window_status}"),
			c.optional(self.task_statuses, self.generate_thread_table),
			c.separator(),
			c.text_colored(f"{self.name} Log:", 'orange'),
			c.child(name=f"{self.name} Log", widget=self.log_widget(self.log), width=-1, height=-1, border=True),
		]))

		for tag, value in events:  # This is how event handling works with `multi_orr`

			if tag == "Information":
				self.information = value

			elif tag == "Start":
				assert self.information
				assert self.process is None
				self.status_queue = Queue()
				self.task_statuses = ["Waiting"] * self.n_tasks
				self.process = Process(target=self.threadify)
				self.process.start()

			elif tag == "Terminate":
				assert self.process is not None
				self.process.terminate()
				self.window_status = "Terminated."
				self.process = None

				for i, status in enumerate(self.task_statuses, 0):
					if status in ["Waiting", "Working..."]:
						self.task_statuses[i] = "Terminated."

			elif tag == "Status Queue":  # Handle events fired by threads.
				# Update the thread state table
				thread_id, new_status = value
				# Update the feature status
				if thread_id < 0:
					self.window_status = new_status
					if new_status == "Work done.":
						self.process = None
				else:
					self.task_statuses[thread_id] = new_status

			elif tag == "Log Queue":
				self.log += value.getMessage() + "\n"

			elif tag == "Number of tasks":
				self.n_tasks = value

			elif tag == "Number of threads":
				self.n_threads = value

			else:
				print(f"Unhandled event: {tag}")

		return self
