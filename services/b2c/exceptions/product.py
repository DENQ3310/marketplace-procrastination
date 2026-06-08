class ProductError(Exception):
	"""Base exception for product-related errors."""


class ProductNotFoundError(ProductError):
	"""Raised when a product is not found."""
