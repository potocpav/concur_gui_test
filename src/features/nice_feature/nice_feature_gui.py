import concur as c

from src.features.nice_feature.nice_feature import do_work


def nice_feature_gui(state, executor):
	key, value = yield from c.window("Nice Feature", c.orr([
		c.button("Nice Feature"),
		c.button("Close"),
		]))

	if key == "Nice Feature":
		if state.future is None:
			print("Starting computation...")
			state.future = executor.submit(do_work, state.work_id)
			state.work_id += 1
			state.window_visible = False
		else:
			print("Computation already running.")

	elif key == "Close":
		state.window_visible = False

	return "Modify State", state
