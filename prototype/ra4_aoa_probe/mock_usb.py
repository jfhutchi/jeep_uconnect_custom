"""Scriptable deterministic USB host used by the host-only AOA model tests."""

from __future__ import annotations

from dataclasses import dataclass

from prototype.ra4_aoa_probe.aoa_transport import (
    ACCESSORY_PIDS,
    ACCESSORY_VID,
    GET_PROTOCOL,
    SEND_STRING,
    START_ACCESSORY,
    UsbDevice,
    UsbEndpoint,
    encode_frame,
)


@dataclass(frozen=True)
class ControlRecord:
    direction: str
    request_type: int
    request: int
    value: int
    index: int
    data: bytes


class MockUsbHost:
    def __init__(
        self,
        *,
        protocol_version: int = 2,
        response_payload: bytes = b"RA4-AOA-PONG",
        fail_control_request: int | None = None,
        fail_string_index: int | None = None,
        detach_times_out: bool = False,
        accessory_vid: int = ACCESSORY_VID,
        accessory_pid: int = min(ACCESSORY_PIDS),
        include_bulk_in: bool = True,
        include_bulk_out: bool = True,
        partial_write: bool = False,
        partial_read: bool = False,
        disconnect_on_read: bool = False,
        fail_release: bool = False,
        initial_device_count: int = 1,
    ) -> None:
        self.protocol_version = protocol_version
        self.response_payload = response_payload
        self.fail_control_request = fail_control_request
        self.fail_string_index = fail_string_index
        self.detach_times_out = detach_times_out
        self.accessory_vid = accessory_vid
        self.accessory_pid = accessory_pid
        self.include_bulk_in = include_bulk_in
        self.include_bulk_out = include_bulk_out
        self.partial_write = partial_write
        self.partial_read = partial_read
        self.disconnect_on_read = disconnect_on_read
        self.fail_release = fail_release
        self.initial_device_count = initial_device_count
        self.control_log: list[ControlRecord] = []
        self.sent_string_indices: list[int] = []
        self.sent_strings: list[bytes] = []
        self.start_requested = False
        self.detach_waited = False
        self.claimed_interfaces: list[int] = []
        self.released_interfaces: list[int] = []
        self.reset_devices: list[str] = []
        self._detached = False
        self._accessory = UsbDevice("accessory-1", accessory_vid, accessory_pid)

    def initial_devices(self) -> tuple[UsbDevice, ...]:
        return tuple(
            UsbDevice(f"phone-{index}", 0x1234, 0x1000 + index)
            for index in range(self.initial_device_count)
        )

    def control_in(
        self,
        device: UsbDevice,
        request_type: int,
        request: int,
        value: int,
        index: int,
        length: int,
        timeout_ms: int,
    ) -> bytes:
        self.control_log.append(
            ControlRecord("in", request_type, request, value, index, bytes(length))
        )
        if request == self.fail_control_request:
            raise OSError("scripted control IN failure")
        if request != GET_PROTOCOL or length != 2:
            raise OSError("unexpected control IN")
        return self.protocol_version.to_bytes(2, "little")

    def control_out(
        self,
        device: UsbDevice,
        request_type: int,
        request: int,
        value: int,
        index: int,
        data: bytes,
        timeout_ms: int,
    ) -> int:
        self.control_log.append(
            ControlRecord("out", request_type, request, value, index, data)
        )
        if request == self.fail_control_request:
            raise OSError("scripted control OUT failure")
        if request == SEND_STRING:
            if index == self.fail_string_index:
                raise OSError("scripted identity failure")
            self.sent_string_indices.append(index)
            self.sent_strings.append(data)
            return len(data)
        if request == START_ACCESSORY:
            self.start_requested = True
            return len(data)
        raise OSError("unexpected control OUT")

    def wait_for_detach(self, device: UsbDevice, timeout_ms: int) -> None:
        self.detach_waited = True
        if self.detach_times_out:
            raise TimeoutError("scripted detach timeout")
        self._detached = True

    def wait_for_accessory(self, timeout_ms: int) -> UsbDevice:
        if not self._detached:
            raise TimeoutError("initial device remains attached")
        return self._accessory

    def select_configuration(self, device: UsbDevice, configuration: int) -> None:
        if configuration != 1:
            raise OSError("only configuration 1 exists")

    def endpoints(self, device: UsbDevice) -> tuple[UsbEndpoint, ...]:
        endpoints: list[UsbEndpoint] = []
        if self.include_bulk_out:
            endpoints.append(UsbEndpoint(0x01, 0, "out", "bulk"))
        if self.include_bulk_in:
            endpoints.append(UsbEndpoint(0x81, 0, "in", "bulk"))
        if device.pid == 0x2D01:
            endpoints.extend(
                (
                    UsbEndpoint(0x02, 1, "out", "bulk"),
                    UsbEndpoint(0x82, 1, "in", "bulk"),
                )
            )
        return tuple(endpoints)

    def claim_interface(self, device: UsbDevice, interface: int) -> None:
        self.claimed_interfaces.append(interface)

    def release_interface(self, device: UsbDevice, interface: int) -> None:
        if self.fail_release:
            raise OSError("scripted release failure")
        self.released_interfaces.append(interface)

    def reset_device(self, device: UsbDevice) -> None:
        self.reset_devices.append(device.identifier)

    def bulk_write(
        self, device: UsbDevice, endpoint: int, data: bytes, timeout_ms: int
    ) -> int:
        return len(data) - 1 if self.partial_write else len(data)

    def bulk_read(
        self, device: UsbDevice, endpoint: int, length: int, timeout_ms: int
    ) -> bytes:
        if self.disconnect_on_read:
            raise OSError("scripted disconnect")
        frame = encode_frame(sequence=1, payload=self.response_payload)
        return frame[:-1] if self.partial_read else frame

    def reconnect(self) -> None:
        self._detached = False
