import datetime
from threading import Thread
import concur as c
from concurrent.futures.thread import ThreadPoolExecutor

from src.features.nice_feature.nice_feature_gui import nice_feature_gui
from src.features.nice_feature.nice_feature import do_work





def app():
	executor = ThreadPoolExecutor(100)
	running_future = None
	i = 0

	while True:
		event, key = yield from c.orr([
			create_main_view(),
			c.tag("Result", c.Block(running_future)) if running_future else c.nothing()
			])

		if event == "Nice Feature":
			if running_future is None:
				print("Starting computation...")
				running_future = executor.submit(do_work, i)
				i += 1
			else:
				print("Computation already running.")

		elif event == "Result":
			running_future = None
			print(f"Done. Result: {key}")

		elif event == "Quit":
			break

		yield


def create_main_view():
	main_window = c.orr([

		c.main_menu_bar(widget=c.orr([
			c.menu(label="File", widget=c.orr([
				c.menu_item("Do things"),
				c.menu_item("Do other things"),
			])),
		])),

		nice_feature_gui(),
		c.button("Quit"),
		c.key_press("Quit", ord('Q'), ctrl=True),
	])

	return main_window


if __name__ == "__main__":
	c.main(widget=app(), name="Nice Application", menu_bar=True)
