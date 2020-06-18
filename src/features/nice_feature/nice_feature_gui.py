import concur as c
from multiprocessing import Process, Queue
from src.features.base.BaseGUI import BaseGUI
from src.features.nice_feature.nice_feature import NiceFeature


class NiceFeatureGUI(BaseGUI):

	def __init__(self):
		super().__init__()

		self.name = "Nice Feature"
		self.n_threads = 10
		self.n_tasks = 20
		self.information = ""

	def render(self):
		# use `multi_orr`, so that concurrent events aren't thrown away
		events = yield from c.window(self.name, c.multi_orr([
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
			# TODO Implement a progress bar based on the amount of running threads
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
				information_dict = {
					'log_queue': self.log_queue,
					'information': self.information
				}
				self.process = Process(target=self.threadify, args=(NiceFeature, information_dict,))
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
