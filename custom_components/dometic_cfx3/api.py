from __future__ import annotations

import ipaddress
import json
import socket
import time
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from .const import (
    DEFAULT_PORT,
    TOPIC_BATTERY_PROTECTION,
    TOPIC_BATTERY_VOLTAGE,
    TOPIC_COMPRESSOR,
    TOPIC_CURRENT_TEMP,
    TOPIC_NAME,
    TOPIC_POWER,
    TOPIC_POWER_SOURCE,
    TOPIC_TARGET_TEMP,
    VALUE_TO_BATTERY_PROTECTION,
    VALUE_TO_POWER_SOURCE,
)


class DometicCfx3Error(Exception):
    """Base Dometic CFX3 API error."""


class DometicCfx3ConnectionError(DometicCfx3Error):
    """Connection failed."""


@dataclass
class DometicCfx3Status:
    name: str | None = None
    current_temperature: float | None = None
    target_temperature: float | None = None
    power: bool | None = None
    battery_voltage: float | None = None
    battery_protection: str | None = None
    compressor: bool | None = None
    power_source: str | None = None
    host: str | None = None
    last_communication: datetime | None = None


def _encode_json(values: list[int]) -> bytes:
    return json.dumps({"ddmp": values}, separators=(",", ":")).encode("ascii") + b"\r"


def _decode_messages(buffer: str) -> tuple[list[list[int]], str]:
    messages: list[list[int]] = []
    while "}" in buffer:
        end = buffer.find("}") + 1
        raw = buffer[:end]
        buffer = buffer[end:]
        try:
            data = json.loads(raw)
            ddmp = data.get("ddmp")
            if isinstance(ddmp, list) and all(isinstance(v, int) for v in ddmp):
                messages.append(ddmp)
        except Exception:
            continue
    return messages, buffer


def _int16_le(payload: list[int]) -> int | None:
    if len(payload) < 2:
        return None
    value = payload[0] | (payload[1] << 8)
    if value >= 0x8000:
        value -= 0x10000
    return value


def _uint16_le(payload: list[int]) -> int | None:
    if len(payload) < 2:
        return None
    return payload[0] | (payload[1] << 8)


def _encode_int16_deci(value: float) -> list[int]:
    raw = int(round(value * 10))
    if raw < 0:
        raw = 0x10000 + raw
    return [raw & 0xFF, (raw >> 8) & 0xFF]


def _decode_ascii(payload: list[int]) -> str | None:
    if not payload:
        return None
    chars = []
    for value in payload:
        if 32 <= value <= 126:
            chars.append(chr(value))
    return "".join(chars) or None


class DometicCfx3Client:
    """Blocking local TCP/DDMP client for Dometic CFX3 coolers."""

    def __init__(self, host: str, port: int = DEFAULT_PORT, timeout: float = 4.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def _connect(self) -> socket.socket:
        try:
            sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            sock.settimeout(0.25)
            return sock
        except OSError as err:
            raise DometicCfx3ConnectionError(f"Could not connect to {self.host}:{self.port}: {err}") from err

    def _send(self, sock: socket.socket, values: list[int]) -> None:
        sock.sendall(_encode_json(values))

    def ping(self) -> bool:
        with self._connect() as sock:
            self._send(sock, [2])
            deadline = time.monotonic() + self.timeout
            buffer = ""
            while time.monotonic() < deadline:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        continue
                    buffer += chunk.decode("ascii", errors="ignore")
                    messages, buffer = _decode_messages(buffer)
                    if [4] in messages:
                        return True
                except socket.timeout:
                    continue
        return False

    def read_topic(self, topic: tuple[int, int, int, int]) -> list[int] | None:
        with self._connect() as sock:
            self._send(sock, [2])
            time.sleep(0.05)
            self._send(sock, [1, *topic])
            deadline = time.monotonic() + self.timeout
            buffer = ""
            while time.monotonic() < deadline:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        continue
                    buffer += chunk.decode("ascii", errors="ignore")
                    messages, buffer = _decode_messages(buffer)
                    for msg in messages:
                        if msg == [2]:
                            self._send(sock, [4])
                            continue
                        if len(msg) >= 5 and msg[0] == 0 and tuple(msg[1:5]) == topic:
                            return msg[5:]
                except socket.timeout:
                    continue
        return None

    def write_topic(self, topic: tuple[int, int, int, int], payload: list[int]) -> None:
        with self._connect() as sock:
            self._send(sock, [0, *topic, *payload])
            # Short read to consume ACK/keepalive without depending on it.
            deadline = time.monotonic() + 0.5
            buffer = ""
            while time.monotonic() < deadline:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        continue
                    buffer += chunk.decode("ascii", errors="ignore")
                    messages, buffer = _decode_messages(buffer)
                    for msg in messages:
                        if msg == [2]:
                            self._send(sock, [4])
                except socket.timeout:
                    continue

    def read_status(self) -> DometicCfx3Status:
        status = DometicCfx3Status()

        name = self.read_topic(TOPIC_NAME)
        if name is not None:
            status.name = _decode_ascii(name)

        current = self.read_topic(TOPIC_CURRENT_TEMP)
        current_raw = _int16_le(current or [])
        if current_raw is not None:
            status.current_temperature = current_raw / 10

        target = self.read_topic(TOPIC_TARGET_TEMP)
        target_raw = _int16_le(target or [])
        if target_raw is not None:
            status.target_temperature = target_raw / 10

        power = self.read_topic(TOPIC_POWER)
        if power:
            status.power = bool(power[0])

        voltage = self.read_topic(TOPIC_BATTERY_VOLTAGE)
        voltage_raw = _uint16_le(voltage or [])
        if voltage_raw is not None and voltage_raw > 0:
            status.battery_voltage = voltage_raw / 10

        protection = self.read_topic(TOPIC_BATTERY_PROTECTION)
        if protection:
            status.battery_protection = VALUE_TO_BATTERY_PROTECTION.get(protection[0])

        compressor = self.read_topic(TOPIC_COMPRESSOR)
        if compressor:
            status.compressor = bool(compressor[0])

        source = self.read_topic(TOPIC_POWER_SOURCE)
        if source:
            status.power_source = VALUE_TO_POWER_SOURCE.get(source[0], str(source[0]))

        status.host = self.host
        status.last_communication = datetime.now(timezone.utc)
        return status

    def set_power(self, enabled: bool) -> None:
        self.write_topic(TOPIC_POWER, [1 if enabled else 0])

    def set_target_temperature(self, temperature: float) -> None:
        self.write_topic(TOPIC_TARGET_TEMP, _encode_int16_deci(temperature))

    def set_battery_protection(self, value: int) -> None:
        if value not in (0, 1, 2):
            raise ValueError("Battery protection must be 0, 1 or 2")
        self.write_topic(TOPIC_BATTERY_PROTECTION, [value])


def probe_host(host: str, port: int = DEFAULT_PORT, timeout: float = 0.6) -> dict[str, Any] | None:
    client = DometicCfx3Client(host, port, timeout=timeout)
    try:
        name_payload = client.read_topic(TOPIC_NAME)
    except DometicCfx3Error:
        return None
    name = _decode_ascii(name_payload or [])
    if not name:
        return None
    return {"host": host, "port": port, "name": name}


def discover_devices(network: str, port: int = DEFAULT_PORT, timeout: float = 0.45, workers: int = 64) -> list[dict[str, Any]]:
    try:
        net = ipaddress.ip_network(network, strict=False)
    except ValueError:
        return []
    hosts = [str(ip) for ip in net.hosts()]
    found: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(probe_host, host, port, timeout): host for host in hosts}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                found.append(result)
    found.sort(key=lambda item: item["host"])
    return found
