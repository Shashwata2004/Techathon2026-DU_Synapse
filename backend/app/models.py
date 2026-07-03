from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DeviceStatus = Literal["ON", "OFF"]
DeviceType = Literal["fan", "light"]
AlertSeverity = Literal["info", "warning", "critical"]


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class Device(ApiModel):
    id: str
    name: str
    room_id: str = Field(alias="roomId")
    room_name: str = Field(alias="roomName")
    type: DeviceType
    status: DeviceStatus
    wattage: int
    current_power: int = Field(alias="currentPower")
    last_changed: datetime = Field(alias="lastChanged")
    on_since: datetime | None = Field(alias="onSince")


class Room(ApiModel):
    id: str
    name: str
    purpose: str
    devices: list[Device]
    fans_on: int = Field(alias="fansOn")
    lights_on: int = Field(alias="lightsOn")
    current_power: int = Field(alias="currentPower")
    active_alerts: list["Alert"] = Field(default_factory=list, alias="activeAlerts")


class Alert(ApiModel):
    id: str
    type: str
    room_id: str = Field(alias="roomId")
    message: str
    severity: AlertSeverity = "warning"
    created_at: datetime = Field(alias="createdAt")
    affected_devices: list[str] = Field(alias="affectedDevices")
    active: bool = True


class UsageResponse(ApiModel):
    total_current_watts: int = Field(alias="totalCurrentWatts")
    room_wise_power: dict[str, int] = Field(alias="roomWisePower")
    estimated_kwh_today: float = Field(alias="estimatedKwhToday")
    active_device_count: int = Field(alias="activeDeviceCount")
    total_device_count: int = Field(alias="totalDeviceCount")
    highest_room: str | None = Field(default=None, alias="highestRoom")


class SystemState(ApiModel):
    rooms: list[Room]
    devices: list[Device]
    total_current_watts: int = Field(alias="totalCurrentWatts")
    room_wise_power: dict[str, int] = Field(alias="roomWisePower")
    estimated_kwh_today: float = Field(alias="estimatedKwhToday")
    active_alerts: list[Alert] = Field(alias="activeAlerts")
    recent_alerts: list[Alert] = Field(alias="recentAlerts")
    active_device_count: int = Field(alias="activeDeviceCount")
    total_device_count: int = Field(alias="totalDeviceCount")
    last_updated: datetime = Field(alias="lastUpdated")


class SetDeviceRequest(BaseModel):
    status: DeviceStatus
