from fastapi import FastAPI

from app.api.captcha_controller import router as captcha_router
from app.api.auth_controller import router as auth_router
from app.exceptions.exception_handler import register_exception_handlers
from app.api.user_controller import router as user_router
from app.api.admin_controller import router as admin_router

app = FastAPI(
    title="Enforcement Authentication Service"
)

register_exception_handlers(app)


# Captcha APIs
app.include_router(
    captcha_router,
    prefix="/api/v1/captcha",
    tags=["Captcha"]
)

# Authentication APIs
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

@app.get("/")
def health_check():
    return {
        "status": "UP"
    }


app.include_router(
    user_router,
    prefix="/api/v1"
)

app.include_router(
    admin_router,
    prefix="/api/v1"
)