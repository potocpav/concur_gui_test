import concur as c
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Process, Queue
import queue
import imgui
from src.features.nice_feature.nice_feature import NiceFeature


class NiceFeatureState(object):
	def __init__(self, visible):
		self.window_visible = visible
		self.n_threads = 10
		self.n_tasks = 20
		self.information = ""

		self.status_queue = Queue()
		self.log_queue = Queue(-1)
		self.task_statuses = None
		self.thread = None
		self.status = "Idle"
		self.log = ""


def threadify(n_threads, n_tasks, information, status_queue, log_queue):
	nice_feature = NiceFeature(feature_information=information, log_queue=log_queue)

	# `-1` signifies that the nice_thread status is returned. This is quite ugly. Maybe use two separate queues?
	status_queue.put((-1, "Running..."))
	executor = ThreadPoolExecutor(n_threads)
	for i in range(n_tasks):
		executor.submit(append_to_queue, status_queue=status_queue, wid=i, feature_object=nice_feature)
	executor.shutdown(wait=True)
	status_queue.put((-1, "Work done."))


# wid = worker id
def append_to_queue(status_queue, wid: int, feature_object: NiceFeature):
	status_queue.put((wid, "Working..."))
	feature_object.run(wid)
	status_queue.put((wid, "Done."))


def thread_table(statuses):
	"""Render a simple table with thread statuses."""
	rows = []
	if statuses:
		for i, status in enumerate(statuses):
			rows.append(c.text(f"{i:3d}: {status}"))
	return c.collapsing_header("Thread status", c.optional(statuses, c.orr, rows), open=True)


# These two widgets are not in Concur, so they show how to add new widgets.

def log_widget(text):
	""" Log widget with auto-scroll. """
	while True:
		imgui.text_unformatted(text)
		if imgui.get_scroll_y() >= imgui.get_scroll_max_y():
			imgui.set_scroll_here(1.0)
		yield


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
		yield


def nice_feature_gui(state, name):
	# use `multi_orr`, so that concurrent events aren't thrown away
	events = yield from c.orr([
		c.window(name, c.multi_orr([
			c.tag("Status Queue", c.listen(state.status_queue)),
			c.tag("Log Queue", c.listen(state.log_queue)),

			c.slider_int("Number of threads", state.n_threads, 1, 100),
			c.slider_int("Number of tasks", state.n_tasks, 1, 1000),
			c.input_text(name="Information, the feature needs", value=state.information, tag="Information"),
			c.button("Terminate") if state.thread
				else validating_button("Start", None if state.information else "Feature information is missing!"),
			c.button("Close Window"),
			c.separator(),

			c.text_colored("Feature status:", 'yellow'),
			c.text(f"{state.status}"),

			thread_table(state.task_statuses),
			])),
		c.window(f"{name} Log", log_widget(state.log)),
		])

	for tag, value in events:  # This is how event handling works with `multi_orr`

		if tag == "Information":
			state.information = value

		elif tag == "Start":
			assert state.information
			assert state.thread is None
			state.status_queue = Queue()
			state.task_statuses = ["Waiting"] * state.n_tasks
			state.thread = Process(target=threadify, args=(state.n_threads, state.n_tasks, state.information, state.status_queue, state.log_queue))
			state.thread.start()

		elif tag == "Terminate":
			assert state.thread is not None
			state.thread.terminate()
			state.status = "Terminated."
			state.thread = None

			for i, status in enumerate(state.task_statuses, 0):
				if status in ["Waiting", "Working..."]:
					state.task_statuses[i] = "Terminated."

		elif tag == "Status Queue":  # Handle events fired by threads.
			# Update the thread state table
			thread_id, new_status = value
			# Update the feature status
			if thread_id < 0:
				state.status = new_status
				if new_status == "Work done.":
					state.thread = None
			else:
				state.task_statuses[thread_id] = new_status

		elif tag == "Log Queue":
			state.log += value.getMessage() + "\n"

		elif tag == "Number of tasks":
			state.n_tasks = value

		elif tag == "Number of threads":
			state.n_threads = value

		elif tag == "Close Window":
			state.window_visible = False

		else:
			print(f"Unhandled event: {tag}")

	return state
