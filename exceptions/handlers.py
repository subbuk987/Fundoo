from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from exceptions.auth import AuthError
from exceptions.orm import UserNotFound, UserAlreadyExist


def register_all_errors(app: FastAPI):
    @app.exception_handler(UserNotFound)
    async def user_not_found_exception_handler(request: Request,
                                               exc: UserNotFound):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail,
                     "METHOD": request.method}
        )

    @app.exception_handler(UserAlreadyExist)
    async def user_already_exist_exception_handler(request: Request,
                                                   exc: UserAlreadyExist):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail,
                     "METHOD": request.method}
        )

    @app.exception_handler(AuthError)
    async def auth_error_handler(request: Request, exc: AuthError):
        return JSONResponse(
            status_code=401,
            content={"detail": exc.message}
        )
