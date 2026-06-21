from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.core.config import settings
from app.core.database import engine, Base, async_session_factory
from app.models.user import User, Role
from app.core.auth import hash_password
from app.api.router import api_router
from app.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default roles and admin user
    async with async_session_factory() as session:
        result = await session.execute(select(Role).where(Role.role_name == "admin"))
        if not result.scalar_one_or_none():
            session.add_all([
                Role(role_name="admin", description="Full platform access"),
                Role(role_name="analyst", description="Vendor risk analysis"),
                Role(role_name="executive", description="Read-only dashboards"),
            ])

        result = await session.execute(select(User).where(User.email == "admin@sentinel.ai"))
        if not result.scalar_one_or_none():
            admin = User(
                email="admin@sentinel.ai",
                password_hash=hash_password("admin123"),
                first_name="Admin",
                role="admin",
            )
            session.add(admin)
        await session.commit()

    yield

    await engine.dispose()


app = FastAPI(
    title="SENTINEL API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )
