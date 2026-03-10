from datetime import datetime

from pydantic import BaseModel


class SensorMeta(BaseModel):
    column: str
    display_name: str
    unit: str


class SensorReading(BaseModel):
    name: str
    display_name: str
    value: float | None
    avg_24h: float | None
    unit: str
    alert_high: float | None
    alert_low: float | None
    in_alert: bool


class SensorCurrentResponse(BaseModel):
    readings: list[SensorReading]
    timestamp: datetime | None
    pause_active: bool


class SensorHistoryPoint(BaseModel):
    label: str
    value: float | None


class SensorHistoryResponse(BaseModel):
    sensor: str
    data: list[SensorHistoryPoint]
