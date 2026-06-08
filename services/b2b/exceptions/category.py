from fastapi import HTTPException, status


class CategoryError(HTTPException):
	def __init__(self, code: str, message: str) -> None:
		super().__init__(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"code": code, "message": message},
		)


class CategoryNotFoundError(CategoryError):
	def __init__(self, message: str = "Category not found") -> None:
		super().__init__(code="INVALID_CATEGORY", message=message)
