from pydantic import BaseModel

from backend.models.sensor import SensorMeta


class RelayMeta(BaseModel):
    id: str
    display_name: str
    table: str
    dt_pairs: int


class RelayState(BaseModel):
    id: str
    display_name: str
    override: str       # "on" | "off" | "auto"
    is_on: bool


class RelayStatesResponse(BaseModel):
    relays: list[RelayState]


class RelayStateUpdate(BaseModel):
    state: str          # "on" | "off" | "auto"


class TimerPair(BaseModel):
    pk: int
    starttime: str | None = None
    stoptime: str | None = None


class MetaResponse(BaseModel):
    sensors: list[SensorMeta]
    relays: list[RelayMeta]
