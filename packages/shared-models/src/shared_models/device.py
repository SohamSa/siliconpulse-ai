"""Device domain model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from shared_models.enums import DeviceType, LifecycleStatus, OperationalStatus


class Device(BaseModel):
    device_id: str
    device_type: DeviceType = DeviceType.GPU
    model_name: str
    manufacturer: str
    manufacturing_batch: str
    serial_number: str
    rack_id: str
    server_id: str
    firmware_version: str
    installation_date: datetime
    manufactured_at: datetime
    age_hours: float = Field(ge=0)
    lifecycle_status: LifecycleStatus = LifecycleStatus.HEALTHY
    operational_status: OperationalStatus = OperationalStatus.ONLINE
    created_at: datetime
    updated_at: datetime
