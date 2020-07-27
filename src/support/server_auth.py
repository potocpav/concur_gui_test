from sys import exit


def auth_with_login_server(user, password):
	# Dummy verification, if any char is a digit, authentication fails.
	if isinstance(user, str) and isinstance(password, str):
		if not any(char.isdigit() for char in list(user)) and not any(char.isdigit() for char in list(password)):
			return True
		else:
			return False
	else:
		return False
