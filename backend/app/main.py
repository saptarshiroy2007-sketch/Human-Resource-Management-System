from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, attendance, auth, documents, leave, profile, salary
from app.core.config import settings


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(leave.router)
app.include_router(salary.router)
app.include_router(profile.router)
app.include_router(documents.router)
app.include_router(admin.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
