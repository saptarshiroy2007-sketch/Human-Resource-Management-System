from fastapi import FastAPI

from app.api import admin, attendance, auth, documents, leave, profile, salary
from app.core.config import settings


app = FastAPI(title=settings.app_name)

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
