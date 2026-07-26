"""Fleet bootstrap for simulated GPU devices."""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

from shared_models.device import Device
from shared_models.enums import DeviceType, LifecycleStatus, OperationalStatus
from shared_utils.ids import gpu_device_id, rack_id, server_id
from telemetry_generator.physics import MODEL_PROFILES, TrueDeviceState


FIRMWARE_VERSIONS = ("1.8.2", "2.1.0", "2.3.1", "2.4.0")
MANUFACTURERS = ("SiliconPulse Silicon", "Northwind Accelerators")
BATCHES = ("BATCH-2023-A", "BATCH-2024-B", "BATCH-2024-C", "BATCH-2025-A")


def build_fleet(
    device_count: int,
    rack_count: int,
    *,
    seed: int,
    ambient_c: float,
) -> tuple[list[Device], dict[str, TrueDeviceState]]:
    rng = random.Random(seed)
    models = list(MODEL_PROFILES.keys())
    now = datetime.now(UTC)
    devices: list[Device] = []
    states: dict[str, TrueDeviceState] = {}

    for i in range(1, device_count + 1):
        device_id = gpu_device_id(i)
        rack_idx = ((i - 1) % rack_count) + 1
        rack = rack_id(rack_idx)
        slot = ((i - 1) // rack_count) + 1
        model_name = models[(i - 1) % len(models)]
        firmware = FIRMWARE_VERSIONS[(i + seed) % len(FIRMWARE_VERSIONS)]
        manufactured = now - timedelta(days=rng.randint(90, 900))
        installed = manufactured + timedelta(days=rng.randint(10, 60))
        age_hours = (now - installed).total_seconds() / 3600.0

        device = Device(
            device_id=device_id,
            device_type=DeviceType.GPU,
            model_name=model_name,
            manufacturer=rng.choice(MANUFACTURERS),
            manufacturing_batch=rng.choice(BATCHES),
            serial_number=f"SN-{device_id}-{seed}",
            rack_id=rack,
            server_id=server_id(rack, slot),
            firmware_version=firmware,
            installation_date=installed,
            manufactured_at=manufactured,
            age_hours=age_hours,
            lifecycle_status=LifecycleStatus.HEALTHY,
            operational_status=OperationalStatus.ONLINE,
            created_at=now,
            updated_at=now,
        )
        devices.append(device)
        profile = MODEL_PROFILES[model_name]
        states[device_id] = TrueDeviceState(
            device_id=device_id,
            rack_id=rack,
            model_name=model_name,
            firmware_version=firmware,
            age_hours=age_hours,
            ambient_temperature_c=ambient_c,
            base_clock_mhz=profile["base_clock"],
            clock_speed_mhz=profile["base_clock"],
            utilization_pct=rng.uniform(40.0, 70.0),
            power_watts=profile["idle_power"] + rng.uniform(80.0, 180.0),
            temperature_c=ambient_c + rng.uniform(28.0, 40.0),
            labels={"rack_id": rack, "server_id": device.server_id},
        )

    return devices, states


def devices_in_rack(devices: list[Device], rack: str) -> list[str]:
    return [d.device_id for d in devices if d.rack_id == rack]
