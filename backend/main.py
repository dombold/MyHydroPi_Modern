from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.routers import meta, relays, sensors, settings, system, timers

app = FastAPI(title="HydroPi API", version="2.0.0")

# CORS — allow Vite dev server during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(meta.router, prefix="/api")
app.include_router(sensors.router, prefix="/api")
app.include_router(relays.router, prefix="/api")
app.include_router(timers.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(system.router, prefix="/api")

# Serve built React SPA (production)
STATIC_DIR = Path(__file__).parent / "static"
_assets_dir = STATIC_DIR / "assets"
if STATIC_DIR.exists() and _assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        return FileResponse(STATIC_DIR / "index.html")
