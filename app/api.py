from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from routes.auth_router import auth_router
from routes.note_router import note_router
from routes.user_route import user_router
from exceptions.handlers import register_all_errors
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from middleware.throttling import limiter, rate_limit_exceeded_handler

version = "v1"

description = """
A REST API for Fundoo - A note making application
"""

version_prefix = f"/api/{version}"

app = FastAPI(
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
    license_info={"name": "MIT License",
                  "url": "https://opensource.org/license/mit"}
)

register_all_errors(app)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router,prefix=f"{version_prefix}/users")
app.include_router(auth_router, prefix=f"{version_prefix}/auth")
app.include_router(note_router, prefix=f"{version_prefix}/notes")
