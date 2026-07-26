"""ID helpers."""

from __future__ import annotations

from uuid import uuid4


def new_id() -> str:
    return str(uuid4())


def gpu_device_id(index: int) -> str:
    return f"GPU-{index:03d}"


def rack_id(index: int) -> str:
    return f"RACK-{index:02d}"


def server_id(rack: str, slot: int) -> str:
    return f"{rack}-SRV-{slot:02d}"
