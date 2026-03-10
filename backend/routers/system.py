import subprocess

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config import settings

router = APIRouter()


class ConfirmBody(BaseModel):
    confirm: bool


@router.post("/system/restart")
def restart(body: ConfirmBody):
    if not body.confirm:
        raise HTTPException(status_code=400, detail="confirm must be true")

    if settings.use_mock:
        return {"status": "restarting", "mock": True}

    subprocess.Popen(["sudo", "shutdown", "-r", "now"])
    return {"status": "restarting"}


@router.post("/system/shutdown")
def shutdown(body: ConfirmBody):
    if not body.confirm:
        raise HTTPException(status_code=400, detail="confirm must be true")

    if settings.use_mock:
        return {"status": "shutting_down", "mock": True}

    subprocess.Popen(["sudo", "shutdown", "-h", "now"])
    return {"status": "shutting_down"}
