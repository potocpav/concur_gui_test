import concur as c
import imgui
from concur.integrations import glfw
from src.features.nice_feature.nice_feature_gui import NiceFeatureGUI
from src.features.settings.settings_gui import SettingsGUI


class State:
	def __init__(self):
		self.nice_feature = NiceFeatureGUI()
		self.settings = SettingsGUI()


class Application:
	def __init__(self):
		self.state = State()
		self.style_choices = {"Dark": imgui.style_colors_dark, "Classic": imgui.style_colors_classic, "Light": imgui.style_colors_light}
		self.style = "Classic"

		c.main(widget=self.run_application(), name="Application", width=1024, height=768, menu_bar=True)

	def __create_main_view(self):
		widgets = list()

		main_menu_bar = c.main_menu_bar(widget=c.orr([
			c.menu(label="File", widget=c.orr([
				c.menu_item(label="Quit", shortcut="CTRL+Q")
			])),
			c.menu("Style", widget=c.orr(
				[c.menu_item(label, selected=self.style == label) for label in self.style_choices],
			)),
		]))
		widgets.append(main_menu_bar)

		features = [
			c.forever(self.state.nice_feature.render),
			c.forever(self.state.settings.render),
		]
		widgets.extend(features)

		shortcuts = [
			c.key_press(name="Quit", key_index=glfw.KEY_Q, ctrl=True)
		]
		widgets.extend(shortcuts)

		return c.orr(widgets)

	def run_application(self):
		# Set configured theme (Default is Dark)
		self.style_choices[self.style]()
		while True:
			tag, value = yield from self.__create_main_view()

			if tag in self.style_choices:
				self.style = tag
				self.style_choices[tag]()

			elif tag == "Quit":
				break
			else:
				print(f"Unhandled event: {tag}")

			yield


if __name__ == "__main__":
	app = Application()
