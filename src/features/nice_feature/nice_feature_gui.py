import concur as c


def nice_feature_gui():
	return c.window("Nice Feature", c.orr([
		c.button("Nice Feature"),
		c.button("Close"),
	]))
