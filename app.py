import datetime
from threading import Thread
import concur as c

from src.features.nice_feature.nice_feature_gui import nice_feature_gui

running_features = list()


def app():
	while True:
		event, key = yield from create_main_view()
		if event == "Nice Feature":
			from src.features.nice_feature.nice_feature import NiceFeature
			t_nice_feature = Thread(target=NiceFeature().run, daemon=True)
			t_nice_feature.start()
			running_features.append({"attack_name": "Token Checker", "timestamp": datetime.datetime.now(), "thread_obj": t_nice_feature})
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
