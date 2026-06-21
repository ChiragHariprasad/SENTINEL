from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, entity: str, entity_id: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity} {entity_id} not found")


class DuplicateError(HTTPException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class ValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)


class UnauthorizedError(HTTPException):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


class ForbiddenError(HTTPException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)
