from pathlib import Path
from sys import exit

import concur as c
import imgui
from concur.integrations import glfw

from src.features.nice_feature.nice_feature_gui import NiceFeatureGUI
from src.features.settings.settings_gui import BaseGUI
from src.features.settings.settings_gui import SettingsGUI
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
		self.is_logged_in = False
		self.flag_quit = False
		self.language = "default"

		if not self.is_logged_in:
			c.main(widget=c.font(self.__initialize_custom_font(), self.__handle_auth()), name="Authentication", width=257, height=166)

		if self.is_logged_in:
			c.main(widget=c.font(self.__initialize_custom_font(), self.run_application()), name="Application", width=1024, height=768, menu_bar=True)

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
				exit(0)

			yield

	def __initialize_custom_font(self):
		# https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/Hack
		font_name = "Hack Regular Nerd Font Complete Mono Windows Compatible.ttf"
		font_file = str(Path(__file__).parent / "src" / "resources" / font_name)
		imgui.create_context()
		io = imgui.get_io()

		# TODO* How would I add all of these, is this even possible or even a good idea?
		glyph_ranges = [io.fonts.get_glyph_ranges_cyrillic(),
						io.fonts.get_glyph_ranges_korean(),
						io.fonts.get_glyph_ranges_japanese(),
						io.fonts.get_glyph_ranges_chinese_full(),
						io.fonts.get_glyph_ranges_latin(),
						io.fonts.get_glyph_ranges_default()]

		if self.language == 'default':
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_default()
		elif self.language == 'cyrillic':
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_cyrillic()
		elif self.language == 'korean':
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_korean()
		elif self.language == 'japanese':
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_japanese()
		elif self.language == 'chinese_full':
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_chinese_full()
		elif self.language == 'latin':
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_latin()
		else:
			glyph_ranges_to_load = io.fonts.get_glyph_ranges_default()

		# TODO(*) I checked https://pyimgui.readthedocs.io/en/latest/guide/using-fonts.html but, there is no information about how to add multiple ranges at once.
		return io.fonts.add_font_from_file_ttf(filename=font_file, size_pixels=14, glyph_ranges=glyph_ranges_to_load)

	def __auth_view(self):
		view = c.orr([
			c.collapsing_header(
				text="Languages",
				widget=c.orr([
					c.radio_button(label='English', active=True if self.language == 'default' else False, tag='english'),
					c.same_line(),
					c.radio_button(label='Russian', active=True if self.language == 'cyrillic' else False, tag='cyrillic'),
					c.same_line(),
					c.radio_button(label='Korean', active=True if self.language == 'korean' else False, tag='korean'),
					c.same_line(),
					c.radio_button(label='Japanese', active=True if self.language == 'japanese' else False, tag='japanese'),
					c.same_line(),
					c.radio_button(label='Chinese', active=True if self.language == 'chinese_full' else False, tag='chinese_full'),
					c.same_line(),
					c.radio_button(label='German', active=True if self.language == 'latin' else False, tag='latin'),
				]), open=True),
			self.custom_spacing(1, 1),
			c.text("Username:"),
			c.same_line(),
			c.lift(lambda: imgui.push_item_width(self.evaluate_field_size(self.username, self.password))),
			c.input_text(name="", value=self.username, tag="username"),
			c.text("Password:"),
			c.same_line(),
			self.obf_input_text(name="", value=self.password, tag="password"),
			c.button("Terminate", tag='terminate') if self.process
			else self.dynamic_popup_button(label="Login", error=self.evaluate_popup_behaviour({'user': self.username, 'password': self.password}), tag='login'),
		])
		return view

	def __handle_auth(self):
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
						self.is_logged_in = True
						break
					else:
						print("Authentication failed")

			elif tag in ['default', 'cyrillic', 'korean', 'japanese', 'chinese_full', 'latin']:
				self.language = tag

			yield


if __name__ == "__main__":
	app = Application()
