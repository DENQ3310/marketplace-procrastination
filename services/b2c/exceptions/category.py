class CategoryError(Exception):
	"""Base exception for category-related errors."""


class CategoryNotFoundError(CategoryError):
	"""Raised when a category is not found."""


class CategoryHierarchyError(CategoryError):
	"""Raised when category hierarchy is broken (e.g. missing parent)."""
