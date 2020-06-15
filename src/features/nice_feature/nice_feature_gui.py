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
		self.information = None

		self.status_queue = queue.SimpleQueue()
		self.task_statuses = None
		self.thread = None
		self.status = "Idle"


def threadify(q, n_threads, n_tasks, _information_the_feature_needs):
	nice_feature = NiceFeature(feature_information=_information_the_feature_needs)

	# `-1` signifies that the nice_thread status is returned. This is quite ugly. Maybe use two separate queues?
	q.put((-1, "Running..."))
	executor = ThreadPoolExecutor(n_threads)
	for i in range(n_tasks):
		executor.submit(append_to_queue, status_queue=q, wid=i, feature_object=nice_feature)
	executor.shutdown(wait=True)
	q.put((-1, "Work done."))


# wid = worker id
def append_to_queue(status_queue, wid: int, feature_object: NiceFeature):
	status_queue.put((wid, "Working..."))
	feature_object.run(wid)
	status_queue.put((wid, "Done."))


# TODO: Make the thread table collapsable
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
		c.input_text(name="Information, the feature needs", value="", tag="feature_information"),
		c.button("Terminate") if state.thread else c.button("Start"),
		c.button("Close Window"),
		c.separator(),

		c.text_colored("Feature status:", 'yellow'),
		c.text(f"{state.status}"),
		c.separator(),

		c.optional(state.task_statuses, thread_table, state.task_statuses),
	]))

	for tag, value in events:  # This is how event handling works with `multi_orr`

		if tag == "feature_information":
			state.information = value

		if tag == "Start":
			if not state.information:  # TODO: The popup does not show up
				imgui.open_popup("Feature information is missing!")
				if imgui.begin_popup("Feature information is missing!"):
					imgui.button("OK")
					imgui.end_popup()
				print("Feature information is missing!")
				continue
			assert state.thread is None
			state.status_queue = Queue()
			state.task_statuses = ["Waiting"] * state.n_tasks
			state.thread = Process(target=threadify, args=(state.status_queue, state.n_threads, state.n_tasks, state.information,))
			state.thread.start()

		elif tag == "Terminate":
			assert state.thread is not None
			state.thread.terminate()
			state.status = "Terminated."
			state.thread = None

			for i, status in enumerate(state.task_statuses, 0):
				if status in ["Waiting", "Working..."]:
					state.task_statuses[i] = "Terminated."

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
