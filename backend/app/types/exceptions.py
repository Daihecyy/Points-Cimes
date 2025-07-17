from typing import Any

from fastapi import HTTPException


class InvalidAppStateTypeError(Exception):
    def __init__(self):
        super().__init__(
            "The type of the app state is not a TypedDict or a starlette State object.",
        )


class ContentHTTPException(HTTPException):
    """
    A custom HTTPException allowing to return custom content.

    Instead of returning `{detail: <content>}`, this exception can return a json serialized `<content>`.

    You need to define a custom exception handler to use it:
    ```python
    @app.exception_handler(ContentHTTPException)
    async def auth_exception_handler(
        request: Request,
        exc: ContentHTTPException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(exc.content),
            headers=exc.headers,
        )
    ```
    """

    def __init__(
        self,
        status_code: int,
        content: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=content, headers=headers)
        self.content = content


class AuthHTTPException(ContentHTTPException):
    """
    A custom HTTPException used for OIDC or OAuth error responses
    """

    def __init__(
        self,
        status_code: int,
        error: str,
        error_description: str,
    ) -> None:
        content = {
            "error": error,
            "error_description": error_description,
        }

        super().__init__(status_code=status_code, content=content)


class UnsetRedirectionUriError(Exception):
    def __init__(self):
        super().__init__("No redirection URI set in the PaymentTool configuration.")


class FileNameIsNotAnUUIDError(Exception):
    def __init__(self):
        super().__init__("The filename is not a valid UUID")


class FileDoesNotExistError(Exception):
    def __init__(self, name: str):
        super().__init__(f"The file {name} does not exist")


class MissingTZInfoInDatetimeError(TypeError):
    def __init__(self):
        super().__init__("tzinfo info is required for datetime objects")


class DotenvMissingVariableError(Exception):
    def __init__(self, variable_name: str):
        super().__init__(f"{variable_name} should be configured in the dotenv")


class DotenvInvalidVariableError(Exception):
    pass


class InvalidRSAKeyInDotenvError(TypeError):
    def __init__(self, actual_key_type: str):
        super().__init__(
            f"RSA_PRIVATE_PEM_STRING in dotenv is not an RSA key but a {actual_key_type}",
        )
