import datetime
from threading import Thread
import concur as c
from concurrent.futures.thread import ThreadPoolExecutor

from src.features.nice_feature.nice_feature_gui import nice_feature_gui
from src.features.nice_feature.nice_feature import do_work


class State:
	def __init__(self):
		self.future = None
		self.window_visible = True
		self.work_id = 0
		self.work_result = None


def app():
	executor = ThreadPoolExecutor(100)
	state = State()

	while True:
		key, value = yield from c.orr([
			create_main_view(state),
			c.optional(state.window_visible, nice_feature_gui),
			c.tag("Result", c.Block(state.future)) if state.future else c.nothing()
			])

		if key == "Nice Feature":
			if state.future is None:
				print("Starting computation...")
				state.future = executor.submit(do_work, state.work_id)
				state.work_id += 1
				state.window_visible = False
			else:
				print("Computation already running.")

		elif key == "Result":
			state.future = None
			state.work_result = value
			print(f"Done. Result: {value}")

		elif key == "Show Window":
			state.window_visible = True
		elif key == "Close":
			state.window_visible = False

		elif key == "Quit":
			break


		yield


def create_main_view(state):
	if state.future:
		status_text = "Working..."
	elif state.work_result is not None:
		status_text = f"Result: {state.work_result}"
	else:
		status_text = ""

	main_window = c.orr([
		c.main_menu_bar(widget=c.orr([
			c.menu(label="File", widget=c.orr([
				c.menu_item("Do things"),
				c.menu_item("Do other things"),
			])),
		])),

		c.button("Show Window"),
		c.text(status_text),
		c.button("Quit"),
		c.key_press("Quit", ord('Q'), ctrl=True),
	])

	return main_window


if __name__ == "__main__":
	c.main(widget=app(), name="Nice Application", menu_bar=True)
