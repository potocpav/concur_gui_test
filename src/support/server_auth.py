from sys import exit


def auth_with_login_server(user, password):
	# Do actual verification here.
	if isinstance(user, str) and isinstance(password, str):
		if not user.isdigit() and not password.isdigit():
			return True
		else:
			print("Not authenthicated.")
			exit(1)
			return False
	else:
		print("Not authenthicated.")
		exit(1)
		return False
