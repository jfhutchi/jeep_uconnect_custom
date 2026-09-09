import unittest

from prototype.ra4_aoa_probe.aoa_transport import (
    ACCESSORY_PIDS,
    ACCESSORY_VID,
    MAX_FRAME_BYTES,
    MAX_PAYLOAD_BYTES,
    AoaIdentity,
    AoaSession,
    AoaState,
    ControlTransferError,
    DetachTimeoutError,
    EndpointDiscoveryError,
    OwnershipConflictError,
    ProtocolVersionError,
    ReenumerationError,
    TransferError,
    UnexpectedStateError,
    decode_frame,
    encode_frame,
)
from prototype.ra4_aoa_probe.mock_usb import MockUsbHost


class AoaTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.identity = AoaIdentity(
            manufacturer="OpenAI Research",
            model="RA4 AOA Probe",
            description="Bounded AOA transport test",
            version="1.0",
            uri="https://example.invalid/ra4-aoa",
            serial="NOT-TARGET-VERIFIED",
        )

    def new_session(self, host: MockUsbHost) -> AoaSession:
        return AoaSession(host=host, identity=self.identity)

    def test_successful_negotiation_and_bidirectional_exchange(self) -> None:
        host = MockUsbHost(response_payload=b"RA4-AOA-PONG")

        result = self.new_session(host).run(b"RA4-AOA-PING")

        self.assertEqual(result.protocol_version, 2)
        self.assertEqual(result.accessory_vid, ACCESSORY_VID)
        self.assertIn(result.accessory_pid, ACCESSORY_PIDS)
        self.assertEqual(result.response_payload, b"RA4-AOA-PONG")
        self.assertEqual(result.final_state, AoaState.RELEASED)
        self.assertEqual(host.claimed_interfaces, [0])
        self.assertEqual(host.released_interfaces, [0])

    def test_protocol_query_failure_stops_before_identity(self) -> None:
        host = MockUsbHost(fail_control_request=51)

        with self.assertRaises(ControlTransferError):
            self.new_session(host).run(b"RA4-AOA-PING")

        self.assertEqual(host.sent_string_indices, [])
        self.assertFalse(host.start_requested)

    def test_unsupported_protocol_version_fails_closed(self) -> None:
        host = MockUsbHost(protocol_version=3)

        with self.assertRaises(ProtocolVersionError):
            self.new_session(host).run(b"RA4-AOA-PING")

        self.assertFalse(host.start_requested)

    def test_control_transfer_failure_aborts_identity_sequence(self) -> None:
        host = MockUsbHost(fail_string_index=3)

        with self.assertRaises(ControlTransferError):
            self.new_session(host).run(b"RA4-AOA-PING")

        self.assertEqual(host.sent_string_indices, [0, 1, 2])
        self.assertFalse(host.start_requested)

    def test_identity_strings_use_exact_order_and_nul_termination(self) -> None:
        host = MockUsbHost()

        self.new_session(host).run(b"RA4-AOA-PING")

        self.assertEqual(host.sent_string_indices, [0, 1, 2, 3, 4, 5])
        self.assertEqual(
            host.sent_strings,
            [value.encode("utf-8") + b"\0" for value in self.identity.values()],
        )

    def test_control_requests_use_exact_aoa_setup_tuples(self) -> None:
        host = MockUsbHost()

        self.new_session(host).run(b"RA4-AOA-PING")

        setup = [
            (record.direction, record.request_type, record.request, record.value, record.index)
            for record in host.control_log
        ]
        self.assertEqual(setup[0], ("in", 0xC0, 51, 0, 0))
        self.assertEqual(
            setup[1:7],
            [("out", 0x40, 52, 0, index) for index in range(6)],
        )
        self.assertEqual(setup[7], ("out", 0x40, 53, 0, 0))

    def test_start_failure_does_not_wait_for_detach(self) -> None:
        host = MockUsbHost(fail_control_request=53)

        with self.assertRaises(ControlTransferError):
            self.new_session(host).run(b"RA4-AOA-PING")

        self.assertFalse(host.detach_waited)

    def test_detach_timeout_is_explicit(self) -> None:
        host = MockUsbHost(detach_times_out=True)

        with self.assertRaises(DetachTimeoutError):
            self.new_session(host).run(b"RA4-AOA-PING")

        self.assertTrue(host.start_requested)

    def test_wrong_reenumerated_vid_pid_is_rejected(self) -> None:
        host = MockUsbHost(accessory_vid=0x1234, accessory_pid=0x5678)

        with self.assertRaises(ReenumerationError):
            self.new_session(host).run(b"RA4-AOA-PING")

        self.assertEqual(host.claimed_interfaces, [])

    def test_missing_accessory_bulk_pair_is_rejected(self) -> None:
        host = MockUsbHost(include_bulk_in=False)

        with self.assertRaises(EndpointDiscoveryError):
            self.new_session(host).run(b"RA4-AOA-PING")

        self.assertEqual(host.claimed_interfaces, [])

    def test_partial_bulk_write_is_an_error_and_releases_interface(self) -> None:
        host = MockUsbHost(partial_write=True)

        with self.assertRaises(TransferError):
            self.new_session(host).run(b"RA4-AOA-PING")

        self.assertEqual(host.released_interfaces, [0])
        self.assertEqual(host.reset_devices, ["accessory-1"])

    def test_partial_bulk_read_is_an_error_and_releases_interface(self) -> None:
        host = MockUsbHost(partial_read=True)

        with self.assertRaises(TransferError):
            self.new_session(host).run(b"RA4-AOA-PING")

        self.assertEqual(host.released_interfaces, [0])
        self.assertEqual(host.reset_devices, ["accessory-1"])

    def test_disconnect_during_transfer_is_an_error(self) -> None:
        host = MockUsbHost(disconnect_on_read=True)

        with self.assertRaises(TransferError):
            self.new_session(host).run(b"RA4-AOA-PING")

        self.assertEqual(host.released_interfaces, [0])
        self.assertEqual(host.reset_devices, ["accessory-1"])

    def test_cleanup_failure_does_not_replace_primary_transfer_error(self) -> None:
        host = MockUsbHost(partial_write=True, fail_release=True)

        with self.assertRaisesRegex(TransferError, "partial bulk OUT"):
            self.new_session(host).run(b"RA4-AOA-PING")

    def test_unexpected_state_reuse_is_rejected(self) -> None:
        session = self.new_session(MockUsbHost())
        session.state = AoaState.EXCHANGING

        with self.assertRaises(UnexpectedStateError):
            session.run(b"RA4-AOA-PING")

    def test_clean_reconnect_can_repeat_the_complete_session(self) -> None:
        host = MockUsbHost(response_payload=b"RA4-AOA-PONG")
        session = self.new_session(host)

        first = session.run(b"RA4-AOA-PING")
        host.reconnect()
        second = session.run(b"RA4-AOA-PING")

        self.assertEqual(first.response_payload, second.response_payload)
        self.assertEqual(host.claimed_interfaces, [0, 0])
        self.assertEqual(host.released_interfaces, [0, 0])

    def test_ambiguous_initial_ownership_is_rejected(self) -> None:
        host = MockUsbHost(initial_device_count=2)

        with self.assertRaises(OwnershipConflictError):
            self.new_session(host).run(b"RA4-AOA-PING")

        self.assertEqual(host.control_log, [])

    def test_framing_is_deterministic_bidirectional_and_crc_checked(self) -> None:
        first = encode_frame(sequence=7, payload=b"RA4-AOA-PING")
        second = encode_frame(sequence=7, payload=b"RA4-AOA-PING")

        self.assertEqual(first, second)
        self.assertEqual(decode_frame(first).sequence, 7)
        self.assertEqual(decode_frame(first).payload, b"RA4-AOA-PING")

        corrupt = bytearray(first)
        corrupt[-1] ^= 0x01
        with self.assertRaises(TransferError):
            decode_frame(bytes(corrupt))

    def test_complete_wire_frame_is_bounded_to_256_bytes(self) -> None:
        largest = encode_frame(sequence=1, payload=b"x" * MAX_PAYLOAD_BYTES)

        self.assertEqual(MAX_FRAME_BYTES, 256)
        self.assertEqual(len(largest), MAX_FRAME_BYTES)
        with self.assertRaises(TransferError):
            encode_frame(sequence=1, payload=b"x" * (MAX_PAYLOAD_BYTES + 1))


if __name__ == "__main__":
    unittest.main()
