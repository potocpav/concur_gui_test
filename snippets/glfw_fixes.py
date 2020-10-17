# 'Fix' input-errors with special keys
class PatchedGlfwRenderer(GlfwRenderer):
	""" Custom variant of Glfwrenderer in PyImGui:

	https://github.com/swistakm/pyimgui/blob/master/imgui/integrations/glfw.py

	This works around the issue that GLFW uses EN_US keyboard to specify the key codes
	in `keyboard_callback`. This meant that keyboard shortcuts were broken on non-querty
	keyboard layouts.

	See https://github.com/ocornut/imgui/issues/2959 for details.
	"""

	def keyboard_callback(self, window, key, scancode, action, mods):
		try:
			_key = key
			if _key < 0x100:
				# Translate characters to the correct keyboard layout.
				key_name = glfw.get_key_name(key, 0)
				if key_name is not None:
					_key = ord(key_name.upper())
			super(PatchedGlfwRenderer, self).keyboard_callback(window, _key, scancode, action, mods)
		except:
			try:
				super(PatchedGlfwRenderer, self).keyboard_callback(window, key, scancode, action, mods)
			except:
				pass


# fix font-scale for retina screens (to l. 121 glfwy.py)
win_w, win_h = glfw.get_window_size(window)
fb_w, fb_h = glfw.get_framebuffer_size(window)
font_scaling_factor = max(float(fb_w) / win_w, float(fb_h) / win_h)
imgui.get_io().font_global_scale /= font_scaling_factor
