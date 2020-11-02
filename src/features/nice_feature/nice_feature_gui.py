from multiprocessing import Process, Queue

import concur as c
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

	def render(self):
		if self.task_statuses:  # Prepare the progress bar
			n_working_or_finished = sum([status in ["Working...", "Done."] for status in self.task_statuses])
			n_total_threads = len(self.task_statuses)
			progress = n_working_or_finished / n_total_threads
			progress_text = f"{n_working_or_finished}/{n_total_threads}"
			progress_bar = self.progress_bar_widget(progress_text, progress)
		else:
			progress_bar = c.nothing()

		# use `multi_orr`, so that concurrent events aren't thrown away
		events = yield from c.window(self.name, c.multi_orr([
			c.text_tooltip("Drag the slider or enter your preferred amount directly to adjust the amount of threads used.", c.text("Number of Threads")),

			c.slider_int(label="", value=self.n_threads, min_value=1, max_value=100, tag='threads'),
			c.same_line(),
			c.lift(lambda: imgui.push_item_width(self.evaluate_field_size(self.n_threads, self.n_tasks))),
			c.interactive_elem(imgui.input_int, "", self.n_threads, tag="threads"),
			c.lift(lambda: imgui.pop_item_width()),

			c.slider_int(label="", value=self.n_tasks, min_value=1, max_value=100, tag='tasks'),
			c.same_line(),
			c.lift(lambda: imgui.push_item_width(self.evaluate_field_size(self.n_threads, self.n_tasks))),
			c.interactive_elem(imgui.input_int, "", self.n_tasks, tag="threads"),
			c.lift(lambda: imgui.pop_item_width()),

			c.input_text(name="Information, the feature needs", value=self.information, tag="info"),
			c.button("Terminate", tag='terminate') if self.process
			else self.dynamic_popup_button("Start", "Feature information is missing. Continue anyway?" if not self.information else self.evaluate_popup_behaviour({'information': True})),
			c.separator(),

			c.text_colored("Feature status:", 'yellow'),
			c.text(f"{self.window_status}"),
			progress_bar,
			c.optional(bool(self.task_statuses), self.generate_thread_table),
			c.separator(),
			c.text_colored(f"{self.name} Log:", 'orange'),

			# c.child(name=f"{self.name} Log", widget=self.log_widget(self.log), width=-1, height=-1, border=True),
			c.window("Log", self.log_widget(self.log)),
			c.tag(tag_name="status_queue", elem=c.listen(self.status_queue)),
			c.tag("log_queue", c.listen(self.log_queue)),
		]))

		for tag, value in events:  # This is how event handling works with `multi_orr`

			if tag == "info":
				self.information = value

			elif tag == "Start":
				assert self.process is None
				self.status_queue = Queue()
				self.task_statuses = ["Waiting"] * self.n_tasks
				information_dict = {
					'log_queue': self.log_queue,
					'information': self.information
				}
				self.process = Process(target=self.threadify, args=(NiceFeature, information_dict,))
				self.process.start()

			elif tag == "terminate":
				assert self.process is not None
				self.process.terminate()
				self.window_status = "Terminated."
				self.process = None

				for i, status in enumerate(self.task_statuses, 0):
					if status in ["Waiting", "Working..."]:
						self.task_statuses[i] = "Terminated."

			elif tag == "status_queue":  # Handle events fired by threads.
				# Update the thread state table
				thread_id, new_status = value
				# Update the feature status
				if thread_id < 0:
					self.window_status = new_status
					if new_status == "Work done.":
						self.process = None
				else:
					self.task_statuses[thread_id] = new_status

			elif tag == "log_queue":
				msg = value.getMessage()

				# Colored logging
				try:
					text, color = msg.split("|")
				except:
					text, color = msg, "white"

				if color == "green":
					rgb_tuple = (0, 255, 0)
				elif color == "red":
					rgb_tuple = (255, 0, 0)
				else:
					rgb_tuple = (255, 255, 255)

				self.log_list.append((text, rgb_tuple))

			elif tag == "tasks":
				self.n_tasks = value

			elif tag == "threads":
				self.n_threads = value

		return self
