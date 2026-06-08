class FavoriteError(Exception):
	"""Base exception for favorite-related errors."""


class FavoriteNotFoundError(FavoriteError):
	"""Raised when a favorite is not found."""


class FavoriteAlreadyExistsError(FavoriteError):
	"""Raised when trying to add a product that's already in favorites."""


class UnauthorizedError(FavoriteError):
	"""Raised when user is not authorized."""


class InvalidParameterError(FavoriteError):
	"""Raised when request parameters are invalid."""
