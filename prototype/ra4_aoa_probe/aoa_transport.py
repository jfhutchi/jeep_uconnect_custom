"""Deterministic host-only model of the bounded RA4 AOA transport experiment."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import struct
from typing import Protocol, Sequence
import zlib


ACCESSORY_VID = 0x18D1
ACCESSORY_PIDS = frozenset({0x2D00, 0x2D01})
GET_PROTOCOL = 51
SEND_STRING = 52
START_ACCESSORY = 53
CONTROL_IN_VENDOR_DEVICE = 0xC0
CONTROL_OUT_VENDOR_DEVICE = 0x40
CONTROL_TIMEOUT_MS = 1_000
DETACH_TIMEOUT_MS = 5_000
REENUMERATION_TIMEOUT_MS = 5_000
BULK_TIMEOUT_MS = 1_000
MAX_IDENTITY_BYTES = 256
FRAME_MAGIC = b"RA4A"
FRAME_VERSION = 1
_FRAME_HEADER = struct.Struct(">4sBIH")
_FRAME_CRC = struct.Struct(">I")
MAX_FRAME_BYTES = 256
MAX_PAYLOAD_BYTES = MAX_FRAME_BYTES - _FRAME_HEADER.size - _FRAME_CRC.size


class AoaError(RuntimeError):
    """Base error for the bounded AOA model."""


class ControlTransferError(AoaError):
    pass


class ProtocolVersionError(AoaError):
    pass


class DetachTimeoutError(AoaError):
    pass


class ReenumerationError(AoaError):
    pass


class EndpointDiscoveryError(AoaError):
    pass


class OwnershipConflictError(AoaError):
    pass


class TransferError(AoaError):
    pass


class UnexpectedStateError(AoaError):
    pass


class AoaState(Enum):
    DETECTING = "detecting"
    QUERYING_PROTOCOL = "querying_protocol"
    SENDING_IDENTITY = "sending_identity"
    STARTING_ACCESSORY = "starting_accessory"
    WAITING_FOR_DETACH = "waiting_for_detach"
    WAITING_FOR_ACCESSORY = "waiting_for_accessory"
    CLAIMING_INTERFACE = "claiming_interface"
    EXCHANGING = "exchanging"
    RELEASED = "released"


@dataclass(frozen=True)
class AoaIdentity:
    manufacturer: str
    model: str
    description: str
    version: str
    uri: str
    serial: str

    def values(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.manufacturer,
            self.model,
            self.description,
            self.version,
            self.uri,
            self.serial,
        )


@dataclass(frozen=True)
class UsbDevice:
    identifier: str
    vid: int
    pid: int


@dataclass(frozen=True)
class UsbEndpoint:
    address: int
    interface: int
    direction: str
    transfer_type: str


@dataclass(frozen=True)
class Frame:
    sequence: int
    payload: bytes


@dataclass(frozen=True)
class AoaResult:
    protocol_version: int
    accessory_vid: int
    accessory_pid: int
    response_payload: bytes
    final_state: AoaState


class UsbHost(Protocol):
    def initial_devices(self) -> Sequence[UsbDevice]: ...

    def control_in(
        self,
        device: UsbDevice,
        request_type: int,
        request: int,
        value: int,
        index: int,
        length: int,
        timeout_ms: int,
    ) -> bytes: ...

    def control_out(
        self,
        device: UsbDevice,
        request_type: int,
        request: int,
        value: int,
        index: int,
        data: bytes,
        timeout_ms: int,
    ) -> int: ...

    def wait_for_detach(self, device: UsbDevice, timeout_ms: int) -> None: ...

    def wait_for_accessory(self, timeout_ms: int) -> UsbDevice: ...

    def select_configuration(self, device: UsbDevice, configuration: int) -> None: ...

    def endpoints(self, device: UsbDevice) -> Sequence[UsbEndpoint]: ...

    def claim_interface(self, device: UsbDevice, interface: int) -> None: ...

    def release_interface(self, device: UsbDevice, interface: int) -> None: ...

    def reset_device(self, device: UsbDevice) -> None: ...

    def bulk_write(
        self, device: UsbDevice, endpoint: int, data: bytes, timeout_ms: int
    ) -> int: ...

    def bulk_read(
        self, device: UsbDevice, endpoint: int, length: int, timeout_ms: int
    ) -> bytes: ...


def encode_frame(sequence: int, payload: bytes) -> bytes:
    if not 0 <= sequence <= 0xFFFFFFFF:
        raise TransferError("frame sequence must fit in an unsigned 32-bit integer")
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise TransferError(f"payload exceeds {MAX_PAYLOAD_BYTES} bytes")
    header = _FRAME_HEADER.pack(FRAME_MAGIC, FRAME_VERSION, sequence, len(payload))
    body = header + payload
    return body + _FRAME_CRC.pack(zlib.crc32(body) & 0xFFFFFFFF)


def decode_frame(data: bytes) -> Frame:
    minimum = _FRAME_HEADER.size + _FRAME_CRC.size
    if len(data) < minimum:
        raise TransferError("short frame")
    magic, version, sequence, payload_length = _FRAME_HEADER.unpack_from(data)
    if magic != FRAME_MAGIC or version != FRAME_VERSION:
        raise TransferError("invalid frame identity or version")
    if payload_length > MAX_PAYLOAD_BYTES:
        raise TransferError("declared payload exceeds the bounded frame limit")
    expected_length = _FRAME_HEADER.size + payload_length + _FRAME_CRC.size
    if len(data) != expected_length:
        raise TransferError(
            f"frame length mismatch: expected {expected_length}, got {len(data)}"
        )
    expected_crc = _FRAME_CRC.unpack_from(data, expected_length - _FRAME_CRC.size)[0]
    actual_crc = zlib.crc32(data[:-_FRAME_CRC.size]) & 0xFFFFFFFF
    if actual_crc != expected_crc:
        raise TransferError("frame CRC mismatch")
    return Frame(sequence=sequence, payload=data[_FRAME_HEADER.size : -_FRAME_CRC.size])


class AoaSession:
    def __init__(self, host: UsbHost, identity: AoaIdentity) -> None:
        self._host = host
        self._identity = identity
        self.state = AoaState.DETECTING

    def run(self, request_payload: bytes) -> AoaResult:
        if self.state == AoaState.RELEASED:
            self.state = AoaState.DETECTING
        elif self.state != AoaState.DETECTING:
            raise UnexpectedStateError(
                f"cannot start a session from state {self.state.value}"
            )
        devices = tuple(self._host.initial_devices())
        if len(devices) != 1:
            raise OwnershipConflictError(
                f"expected exactly one eligible initial device, found {len(devices)}"
            )
        initial = devices[0]
        protocol_version = self._query_protocol(initial)
        self._send_identity(initial)
        self._start_accessory(initial)

        self._transition(AoaState.STARTING_ACCESSORY, AoaState.WAITING_FOR_DETACH)
        try:
            self._host.wait_for_detach(initial, DETACH_TIMEOUT_MS)
        except TimeoutError as error:
            raise DetachTimeoutError("device did not detach after START_ACCESSORY") from error

        self._transition(AoaState.WAITING_FOR_DETACH, AoaState.WAITING_FOR_ACCESSORY)
        try:
            accessory = self._host.wait_for_accessory(REENUMERATION_TIMEOUT_MS)
        except TimeoutError as error:
            raise ReenumerationError("accessory device did not re-enumerate") from error
        if accessory.vid != ACCESSORY_VID or accessory.pid not in ACCESSORY_PIDS:
            raise ReenumerationError(
                f"unexpected accessory identity {accessory.vid:04X}:{accessory.pid:04X}"
            )

        try:
            self._host.select_configuration(accessory, 1)
        except OSError as error:
            raise EndpointDiscoveryError("could not select accessory configuration 1") from error
        interface, bulk_out, bulk_in = self._find_bulk_pair(accessory)

        self._transition(AoaState.WAITING_FOR_ACCESSORY, AoaState.CLAIMING_INTERFACE)
        try:
            self._host.claim_interface(accessory, interface)
        except OSError as error:
            raise OwnershipConflictError(
                f"could not claim accessory interface {interface}"
            ) from error

        primary_error: AoaError | None = None
        try:
            self._transition(AoaState.CLAIMING_INTERFACE, AoaState.EXCHANGING)
            outbound = encode_frame(sequence=1, payload=request_payload)
            try:
                written = self._host.bulk_write(
                    accessory, bulk_out.address, outbound, BULK_TIMEOUT_MS
                )
            except (OSError, TimeoutError) as error:
                raise TransferError("bulk OUT failed") from error
            if written != len(outbound):
                raise TransferError(
                    f"partial bulk OUT: expected {len(outbound)}, wrote {written}"
                )
            try:
                inbound = self._host.bulk_read(
                    accessory, bulk_in.address, MAX_FRAME_BYTES, BULK_TIMEOUT_MS
                )
            except (OSError, TimeoutError) as error:
                raise TransferError("bulk IN failed") from error
            response = decode_frame(inbound)
            if response.sequence != 1:
                raise TransferError(
                    f"response sequence mismatch: expected 1, got {response.sequence}"
                )
        except AoaError as error:
            primary_error = error
            raise
        finally:
            if primary_error is not None:
                try:
                    self._host.reset_device(accessory)
                except (OSError, TimeoutError):
                    pass
            try:
                self._host.release_interface(accessory, interface)
            except (OSError, TimeoutError):
                if primary_error is None:
                    raise TransferError("failed to release accessory interface")
            self._transition(AoaState.EXCHANGING, AoaState.RELEASED)

        return AoaResult(
            protocol_version=protocol_version,
            accessory_vid=accessory.vid,
            accessory_pid=accessory.pid,
            response_payload=response.payload,
            final_state=self.state,
        )

    def _query_protocol(self, device: UsbDevice) -> int:
        self._transition(AoaState.DETECTING, AoaState.QUERYING_PROTOCOL)
        try:
            response = self._host.control_in(
                device,
                CONTROL_IN_VENDOR_DEVICE,
                GET_PROTOCOL,
                0,
                0,
                2,
                CONTROL_TIMEOUT_MS,
            )
        except (OSError, TimeoutError) as error:
            raise ControlTransferError("GET_PROTOCOL failed") from error
        if len(response) != 2:
            raise ControlTransferError(
                f"GET_PROTOCOL returned {len(response)} bytes instead of 2"
            )
        version = int.from_bytes(response, "little")
        if version not in (1, 2):
            raise ProtocolVersionError(f"unsupported AOA protocol version {version}")
        return version

    def _send_identity(self, device: UsbDevice) -> None:
        self._transition(AoaState.QUERYING_PROTOCOL, AoaState.SENDING_IDENTITY)
        for index, value in enumerate(self._identity.values()):
            data = value.encode("utf-8") + b"\0"
            if len(data) > MAX_IDENTITY_BYTES:
                raise ControlTransferError(
                    f"identity string {index} exceeds {MAX_IDENTITY_BYTES} bytes"
                )
            try:
                written = self._host.control_out(
                    device,
                    CONTROL_OUT_VENDOR_DEVICE,
                    SEND_STRING,
                    0,
                    index,
                    data,
                    CONTROL_TIMEOUT_MS,
                )
            except (OSError, TimeoutError) as error:
                raise ControlTransferError(f"SEND_STRING {index} failed") from error
            if written != len(data):
                raise ControlTransferError(
                    f"SEND_STRING {index} was partial: {written} of {len(data)} bytes"
                )

    def _start_accessory(self, device: UsbDevice) -> None:
        self._transition(AoaState.SENDING_IDENTITY, AoaState.STARTING_ACCESSORY)
        try:
            written = self._host.control_out(
                device,
                CONTROL_OUT_VENDOR_DEVICE,
                START_ACCESSORY,
                0,
                0,
                b"",
                CONTROL_TIMEOUT_MS,
            )
        except (OSError, TimeoutError) as error:
            raise ControlTransferError("START_ACCESSORY failed") from error
        if written != 0:
            raise ControlTransferError(
                f"START_ACCESSORY unexpectedly transferred {written} bytes"
            )

    def _find_bulk_pair(
        self, device: UsbDevice
    ) -> tuple[int, UsbEndpoint, UsbEndpoint]:
        by_interface: dict[int, list[UsbEndpoint]] = {}
        for endpoint in self._host.endpoints(device):
            if endpoint.transfer_type == "bulk":
                by_interface.setdefault(endpoint.interface, []).append(endpoint)
        for interface in sorted(by_interface):
            endpoints = by_interface[interface]
            bulk_out = next(
                (endpoint for endpoint in endpoints if endpoint.direction == "out"), None
            )
            bulk_in = next(
                (endpoint for endpoint in endpoints if endpoint.direction == "in"), None
            )
            if bulk_out is not None and bulk_in is not None:
                return interface, bulk_out, bulk_in
        raise EndpointDiscoveryError("no accessory interface has bulk IN and OUT")

    def _transition(self, expected: AoaState, next_state: AoaState) -> None:
        if self.state != expected:
            raise UnexpectedStateError(
                f"expected state {expected.value}, found {self.state.value}"
            )
        self.state = next_state
