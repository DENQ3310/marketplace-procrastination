class SellerError(Exception):
	"""Base exception for seller-related errors"""


class SellerAlreadyExistsError(SellerError):
	"""Raised if seller already exists"""


class SellerNotFoundError(SellerError):
	"""Raised when seller is not found"""


class InvalidPasswordError(SellerError):
	"""Speaks for itself, doesn't it?"""
