import datetime
from threading import Thread, activeCount
import concur as c
from concurrent.futures.thread import ThreadPoolExecutor

from src.features.nice_feature.nice_feature_gui import nice_feature_gui


class State:
	def __init__(self):
		self.future = None
		self.window_visible = True
		self.work_id = 0
		self.work_result = None


executor = ThreadPoolExecutor(100)


def app():
	state = State()
	while True:
		key, value = yield from create_main_view(state)

		if key == "Show Window":
			state.window_visible = True

		# This can't be in `nice_feature_gui`, because it is not called when the window not shown.
		# There is a workaround for that, but I'm not sure if it even belongs to `nice_feature_gui`.
		elif key == "Result":
			state.future = None
			state.work_result = value
			print(f"Done. Result: {value}")

		# This is not strictly necessary, but may be useful for the Undo operation or something.
		elif key == "Modify State":
			state = value

		elif key == "Active Threads":
			print(activeCount())

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

	return c.orr([
		c.main_menu_bar(widget=c.orr([
			c.menu(label="File", widget=c.orr([
				c.menu_item("Do things"),
				c.menu_item("Do other things"),
			])),
		])),

		c.optional(state.window_visible, nice_feature_gui, state, executor),
		c.tag("Result", c.optional(state.future, c.Block, state.future)),

		c.button("Show Window"),
		c.text(status_text),
		c.button("Active Threads"),
		c.button("Quit"),
		c.key_press("Quit", ord('Q'), ctrl=True),
	])


if __name__ == "__main__":
	c.main(widget=app(), name="Nice Application", menu_bar=True)
