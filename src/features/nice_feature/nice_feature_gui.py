from multiprocessing import Process, Queue

import concur as c

from src.features.base.BaseGUI import BaseGUI
from src.features.nice_feature.nice_feature import NiceFeature


def progress_bar_widget(text, progress):
	""" Progress bar widget. """

	# This widget is based off of `PanZoom`, which is a powerful pannable-zoomable canvas.
	# It is certainly an overkill, because I use it just for the convenient sizing and transformation.
	# The widget could be written quite easily using plain ImGUI calls instead. But this is easier for me.
	#
	# Additional colors could be added quite easily, using `rect_filled` with different colors.
	def overlay(tf, event_gen):
		return c.orr([
			c.draw.rect_filled(0, 0, progress, 1, 0xff753b3b, tf=tf),
			c.draw.text(text, 0.4, 0.2, 'white', tf=tf),
		])

	# The progress bar coordinate system is between (0, 1) in both axes (x, y).
	pz = c.PanZoom((0, 0), (1, 1), False)
	return c.forever(c.extra_widgets.pan_zoom, "", pz, None, 20, content_gen=overlay)


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
			progress_bar = progress_bar_widget(progress_text, progress)
		else:
			progress_bar = c.nothing()

		# use `multi_orr`, so that concurrent events aren't thrown away
		events = yield from c.window(self.name, c.multi_orr([
			c.tag(tag_name="Status Queue", elem=c.listen(self.status_queue)),
			c.tag("Log Queue", c.listen(self.log_queue)),
			c.slider_int("Number of threads", self.n_threads, 1, 100),
			c.same_line(),
			c.drag_int("Number of threads", self.n_threads),
			c.slider_int("Number of tasks  ", self.n_tasks, 1, 1000),
			c.same_line(),
			c.drag_int("Number of tasks", self.n_tasks),
			c.input_text(name="Information, the feature needs", value=self.information, tag="Information"),
			c.button("Terminate") if self.process
			else self.validating_button("Start",
										None if self.information
										else "Feature information is missing. Continue anyway?"),
			c.separator(),

			c.text_colored("Feature status:", 'yellow'),
			c.text(f"{self.window_status}"),
			progress_bar,
			c.optional(self.task_statuses, self.generate_thread_table),
			c.separator(),
			c.text_colored(f"{self.name} Log:", 'orange'),
			c.child(name=f"{self.name} Log", widget=self.log_widget(self.log), width=-1, height=-1, border=True),
		]))

		for tag, value in events:  # This is how event handling works with `multi_orr`

			if tag == "Information":
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

			elif tag == "Number of tasks":
				self.n_tasks = value

			elif tag == "Number of threads":
				self.n_threads = value

			else:
				print(f"Unhandled event: {tag}")

		return self
