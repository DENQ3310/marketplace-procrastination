class InvoiceError(Exception):
	"""Basic exception for invoices"""


class InvoiceNotFoundError(InvoiceError):
	"""Basic exception when an invoice is not found in the database."""


class InvalidInvoiceStatusError(InvoiceError):
	"""Basic exception when attempting to perform an action that is not available for the current status."""


class EmptyInvoiceError(InvoiceError):
	"""Basic exception if there are no items in the invoice"""


class InvoiceSkuNotModeratedError(InvoiceError):
	"""Raised when an invoice contains a SKU of a non-moderated product."""


class InvoiceSkuNotOwnerError(InvoiceError):
	"""Raised when an invoice contains another seller's SKU."""
