from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from exceptions.auth import AuthError
from routes.auth_router import auth_router
from utils.lifespan import lifespan
from routes.user_route import user_router
from exceptions.orm import UserAlreadyExist, UserNotFound

app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(auth_router)


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