class BaseS3Error(Exception):
	"""Basic S3-related error"""


class S3UnallowedFileTypeError(BaseS3Error):
	"""Raised when disallowed filetype is being placed in s3 storage"""


class S3FileTooBigError(BaseS3Error):
	"""Raised when loaded file is too big"""


class S3InternalError(BaseS3Error):
	"""Raised when some error that i don't control occures"""
