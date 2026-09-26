from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.bookings import router as bookings_router
from app.api.centres import router as centres_router
from app.api.payments import router as payments_router
from app.api.tests import router as tests_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Backend API service for EVE Healthcare Diagnostic Test Bookings and Simulated Payments. "
        "Supports JWT Authentication, Centre/Test Management, Booking Workflows, and Idempotent Webhook Payments."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Exception handler for validation errors to format response cleanly
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Validation error in request payload",
        },
    )


# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(centres_router, prefix=settings.API_V1_STR)
app.include_router(tests_router, prefix=settings.API_V1_STR)
app.include_router(bookings_router, prefix=settings.API_V1_STR)
app.include_router(payments_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "healthy",
        "documentation": "/docs",
    }
