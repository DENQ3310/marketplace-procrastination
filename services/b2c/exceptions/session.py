class SessionError(Exception):
	"""Base exception for session errors"""


class SessionNotFoundError(SessionError):
	"""Error if session is not found"""
