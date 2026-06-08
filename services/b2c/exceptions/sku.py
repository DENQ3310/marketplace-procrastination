class SkuError(Exception):
	"""Base exception for SKU-related errors."""


class SkuNotFoundError(SkuError):
	"""Raised when a SKU is not found."""
