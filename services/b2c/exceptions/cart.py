class CartError(Exception):
	"""Base exception for cart operations"""

	pass


class MissingCartIdentityError(CartError):
	"""Raised when neither X-User-Id nor X-Session-Id is provided"""

	pass


class InvalidSessionIdError(CartError):
	"""Raised when the session ID is invalid"""

	pass


class CartItemNotFoundError(CartError):
	"""Raised when a cart item is not found"""

	pass


class InsufficientStockError(CartError):
	"""Raised when the requested quantity is not available"""

	pass


class SkuUnavailableError(CartError):
	"""Raised when the SKU is unavailable"""

	pass
