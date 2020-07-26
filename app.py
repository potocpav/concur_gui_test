from pathlib import Path
from sys import exit

import concur as c
import imgui
from concur.integrations import glfw

from src.features.nice_feature.nice_feature_gui import NiceFeatureGUI
from src.features.settings.settings_gui import SettingsGUI
from src.features.settings.settings_gui import BaseGUI
from src.support.server_auth import auth_with_login_server


class State:
	def __init__(self):
		self.nice_feature = NiceFeatureGUI()
		self.settings = SettingsGUI()


class Application(BaseGUI):
	def __init__(self):
		super().__init__()
		self.state = State()
		self.style_choices = {"Dark": imgui.style_colors_dark, "Classic": imgui.style_colors_classic, "Light": imgui.style_colors_light}
		self.style = "Classic"
		self.username = ""
		self.password = ""
		self.glyph_ranges = None
		self.language_dict = {
			'default': True,
			'latin': False,
			'cyrillic': False,
			'korean': False,
			'japanese': False,
			'chinese_full': False
		}
		self.font = self.__initialize_custom_font()
		c.main(widget=c.font(self.font, self.auth()), name="Authentication", width=257, height=166)
		self.font = self.__initialize_custom_font()  # TODO Apparently I have to initialize the font again, else I will get an assertion error.
		c.main(widget=c.font(self.font, self.run_application()), name="Application", width=1024, height=768, menu_bar=True)

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

	def __initialize_custom_font(self):
		font_name = "Hack Regular Nerd Font Complete Mono Windows Compatible.ttf"
		font_file = str(Path(__file__).parent / "src" / "resources" / font_name)
		imgui.create_context()
		io = imgui.get_io()

		# How would I add all of these, is this even possible?
		glyph_ranges = [io.fonts.get_glyph_ranges_cyrillic(),
						io.fonts.get_glyph_ranges_korean(),
						io.fonts.get_glyph_ranges_japanese(),
						io.fonts.get_glyph_ranges_chinese_full(),
						io.fonts.get_glyph_ranges_latin(),
						io.fonts.get_glyph_ranges_default()]

		if self.language_dict['default']:
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_default()
		elif self.language_dict['cyrillic']:
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_cyrillic()
		elif self.language_dict['korean']:
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_korean()
		elif self.language_dict['japanese']:
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_japanese()
		elif self.language_dict['chinese_full']:
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_chinese_full()
		elif self.language_dict['latin']:
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_latin()
		else:
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_default()

		# TODO I checked https://pyimgui.readthedocs.io/en/latest/guide/using-fonts.html but, there is no information about how to add multiple ranges at once.
		return io.fonts.add_font_from_file_ttf(filename=font_file, size_pixels=14, glyph_ranges=glyph_ranges_to_load)

	def auth(self):
		self.style_choices[self.style]()
		while True:
			tag, value = yield from self.__auth_view()
			if tag in "username":
				self.username = value
			elif tag in "password":
				self.password = value
			elif tag in "login":
				if self.username != "" and self.password != "":
					if auth_with_login_server(self.username, self.password):
						print("Logging in with", "User: ", self.username, "Password: ", self.password)
						break
					else:
						print("Not authenthicated.")
						exit(1)
				else:
					print("Provide login credentials before you login.")
			# TODO: Is there a way to get the current status of the collapsing_header() and change the window size, depending on if it is opened or closed?
			# imgui.set_next_window_size(257, 166)   # Expanded
			# imgui.set_next_window_size(225, 113)   # Collapsed

			elif tag in "default":
				for key in self.language_dict.keys():
					self.language_dict[key] = False
				self.language_dict['default'] = True
			elif tag in "cyrillic":
				for key in self.language_dict.keys():
					self.language_dict[key] = False
				self.language_dict['cyrillic'] = True
			elif tag in "korean":
				for key in self.language_dict.keys():
					self.language_dict[key] = False
				self.language_dict['korean'] = True
			elif tag in "japanese":
				for key in self.language_dict.keys():
					self.language_dict[key] = False
				self.language_dict['japanese'] = True
			elif tag in "chinese_full":
				for key in self.language_dict.keys():
					self.language_dict[key] = False
				self.language_dict['chinese_full'] = True
			elif tag in "german":
				for key in self.language_dict.keys():
					self.language_dict[key] = False
				self.language_dict['latin'] = True

			else:
				print(f"Unhandled event: {tag}")
			yield

	def __auth_view(self):
		view = c.orr([
			c.collapsing_header(
				text="Languages",
				widget=c.orr([c.radio_button(label='English', active=self.language_dict['default'], tag='default'),
							  c.same_line(),
							  c.radio_button(label='Russian', active=self.language_dict['cyrillic'], tag='cyrillic'),
							  c.same_line(),
							  c.radio_button(label='Korean', active=self.language_dict['korean'], tag='korean'),
							  c.radio_button(label='Japanese', active=self.language_dict['japanese'], tag='japanese'),
							  c.same_line(),
							  c.radio_button(label='Chinese', active=self.language_dict['chinese_full'], tag='chinese_full'),
							  c.same_line(),
							  c.radio_button(label='German', active=self.language_dict['latin'], tag='german'),
							  ]),
				open=True),
			c.spacing(),
			c.text("Username:"),
			c.same_line(),
			c.lift(lambda: imgui.push_item_width(self.evaluate_field_size(self.username, self.password))),
			c.input_text(name="", value=self.username, tag="username"),
			c.text("Password:"),
			c.same_line(),
			c.input_text(name="", value=self.password, tag="password"),
			c.button("Login", tag="login"),
		])
		return view


if __name__ == "__main__":
	app = Application()
