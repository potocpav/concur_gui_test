from platform import system

import concur as c
import imgui

from src.features.base.BaseGUI import BaseGUI


class SettingsGUI(BaseGUI):
	def __init__(self):
		super().__init__()
		self.name = "Settings"
		self.style_choices = {"Dark": imgui.style_colors_dark, "Classic": imgui.style_colors_classic, "Light": imgui.style_colors_light}
		self.style = "Dark"
		self.information = ""
		self.filepath = ""
		self.username = ""
		self.password = ""
		self.remember_credentials = False

	def render(self):
		events = yield from c.window(title=self.name, widget=c.multi_orr([
			c.text("Style: "),
			c.orr_same_line([c.radio_button(label, active=self.style == label) for label in self.style_choices]),
			c.spacing(),
			c.text("Username: "),
			c.same_line(),

			# The `c.lift` call is a way to "inject" ImGui calls into the rendering routine.
			# It may be better to abstract these `lift` calls out into a function (or not).
			# Note that Concur (and ImGui as a whole) are primarily made for debug interfaces, so custom styling like this is a bit clunky.
			# The calls used for sizing are [documented here](https://pyimgui.readthedocs.io/en/latest/reference/imgui.core.html).
			# You can do a whole lot of customization like this, I recommend skimming through the above link.
			c.lift(lambda: imgui.push_item_width(100)),
			c.input_text(name="", value=self.username, tag="Username", buffer_length=10),
			c.text("Password: "),
			c.same_line(),

			self.obf_input_text(name="", value=self.password, tag="Password"),
			c.lift(lambda: imgui.pop_item_width()),
			c.checkbox("Remember credentials", self.remember_credentials),
			c.spacing(),
			c.text("Input file: "),
			c.same_line(),
			c.text(self.filepath),
			c.button("Open"),
			self.custom_spacing(0, 20),
			c.separator(),
			c.button("Save"),
			c.same_line(),
			c.button("Reset"),
		]))

		for tag, value in events:  # This is how event handling works with `multi_orr`
			if tag in self.style_choices:
				self.style = tag
				self.style_choices[tag]()
			elif tag == "Open":
				self.prompt_for_input_file()
			elif tag == "Username":
				self.username = value
			elif tag == "Password":
				self.password = value
			elif tag == "Remember credentials":
				self.remember_credentials = value
			elif tag == "Save":
				print("Saved")
			elif tag == "Reset":
				print("Resetted")

		return self

	# wxPython required, if installation throws errors, try with easy_install, if that also fails a linux package is missing.
	# sudo apt install dpkg-dev build-essential freeglut3-dev libgl1-mesa-dev libgl1-mesa-dev libglu1-mesa-dev libgstreamer-plugins-base1.0-dev libgtk-3-dev libjpeg-dev libnotify-dev libpng-dev libsdl2-dev libsm-dev libtiff-dev libxtst-dev libwebkit2gtk-4.0-dev libsecret-1-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
	def prompt_for_input_file(self):
		if "Linux" in system():
			import wx
			_app = wx.App(None)
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
			dialog = wx.FileDialog(None, 'Open', style=style)
			if dialog.ShowModal() == wx.ID_OK:
				self.filepath = dialog.GetPath()
			else:
				self.filepath = ""
			dialog.Destroy()

		elif "Windows" in system():
			import win32gui, win32con, os
			try:
				self.filepath, customfilter, flags = win32gui.GetOpenFileNameW(
					InitialDir=os.environ['temp'],
					Flags=win32con.OFN_EXPLORER,
				)
			except Exception:
				print("File could not be selected")
				return
		else:
			print("OS could not be determined")
			return
