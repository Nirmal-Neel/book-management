from fastapi.exceptions import HTTPException as FastAPIHTTPException


class HTTPException(FastAPIHTTPException):

    def __init__(self, status_code: int, message: str):
        super().__init__(status_code)
        self.message = message
