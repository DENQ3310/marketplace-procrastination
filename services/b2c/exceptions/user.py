class UserError(Exception):
	"""Base exception for user-related errors."""


class UserAlreadyExistsError(UserError):
	"""Raised when a user with the given username or email already exists."""


class UserPasswordTooWeakError(UserError):
	"""Raised when the provided password does not meet the required complexity."""


class InvalidPasswordError(UserError):
	"""Raised when the provided password is incorrect."""


class UserNotFoundError(UserError):
	"""Raised when a user is not found in the database."""


class UserLoginConflictError(UserError):
	"""Raised when both email and username are provided for login, which is not allowed."""


class UserInvalidPasswordError(UserError):
	"""Raised when the provided password is incorrect."""
