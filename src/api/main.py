from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.api.routes.arm import router as arm_router
from src.api.routes.compare import router as compare_router
from src.api.routes.fixed import router as fixed_router
from src.api.routes.health import router as health_router

app = FastAPI(title="Home Loan Pricing Engine", version="1.0.0")

api = FastAPI()

api.include_router(health_router)
api.include_router(fixed_router)
api.include_router(arm_router)
api.include_router(compare_router)


@api.exception_handler(ValidationError)
async def validation_error_handler(request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


app.mount("/api/v1", api)
