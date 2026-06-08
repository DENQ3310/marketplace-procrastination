class SessionError(Exception):
	"""Base session-related error"""


class SessionNotFoundError(SessionError):
	"""Raised when session is not found"""
