from pathlib import Path
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
			# c.same_line(),
			c.orr([c.radio_button(label, active=self.style == label) for label in self.style_choices]),  # TODO: Can the buttons be aligned horizontally, instead of vertically?
			c.spacing(),
			c.text("Username: "),
			c.same_line(),
			c.input_text(name="", value=self.username, tag="Username", buffer_length=10),  # TODO Can size of the textfield, that is being displayed in the GUI be changed?
			c.text("Password: "),
			c.same_line(),
			c.input_text(name="", value=self.password, tag="Password"),  # TODO Can I obfuscate whats in here in the GUI, so that it would only show '****'
			c.checkbox("Remember credentials", self.remember_credentials),
			c.spacing(),
			c.text("Input file: "),
			c.same_line(),
			c.text(self.filepath),
			c.button("Open"),
			c.spacing(), c.spacing(), c.spacing(),  # TODO Is there a nicer way to customize the amount of space being generated?
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
			else:
				print(f"Unhandled event: {tag}")

		return self

	# wxPython required, if installation throws errors, try with easy_install, if that also fails a linux package is missing
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

