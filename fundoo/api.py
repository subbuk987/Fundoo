from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from exceptions.handlers import register_all_errors
from middleware.throttling import limiter, rate_limit_exceeded_handler
from routes.auth_router import auth_router
from routes.note_router import note_router
from routes.user_route import user_router

version = "v1"

description = """
A REST API for Fundoo - A note making application
"""

version_prefix = f"/api/{version}"

fundoo_api = FastAPI(
    title="Fundoo",
    version=version,
    description=description,
    contact={
        "name": "Kandlagunta Subramanyam",
        "url": "https://github.com/subbuk987",
        "email": "subramanyamk2003@gmail.com",
    },
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc",
    openapi_url=f"{version_prefix}/openapi.json",
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
)

register_all_errors(fundoo_api)

fundoo_api.state.limiter = limiter
fundoo_api.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
fundoo_api.add_middleware(SlowAPIMiddleware)


fundoo_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fundoo_api.include_router(user_router, prefix=f"{version_prefix}/users")
fundoo_api.include_router(auth_router, prefix=f"{version_prefix}/auth")
fundoo_api.include_router(note_router, prefix=f"{version_prefix}/notes")
