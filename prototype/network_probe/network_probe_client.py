"""Send one bounded diagnostic message to NetworkProbeXlet."""

from __future__ import annotations

import argparse
import socket
import sys


MAX_MESSAGE_BYTES = 256
MAX_REPLY_BYTES = 128


class ProbeClientError(RuntimeError):
    """Raised when the bounded request/response exchange cannot complete."""


def _encode_message(message: str) -> bytes:
    try:
        payload = message.encode("ascii")
    except UnicodeEncodeError as error:
        raise ProbeClientError("message must contain printable ASCII only") from error
    if not payload:
        raise ProbeClientError("message must not be empty")
    if len(payload) > MAX_MESSAGE_BYTES:
        raise ProbeClientError("message exceeds 256 ASCII bytes")
    if any(value < 32 or value > 126 for value in payload):
        raise ProbeClientError("message must contain printable ASCII only")
    return payload


def exchange(host: str, port: int, message: str, timeout: float = 5.0) -> str:
    payload = _encode_message(message)
    try:
        with socket.create_connection((host, port), timeout=timeout) as connection:
            connection.settimeout(timeout)
            connection.sendall(payload + b"\n")
            reply = bytearray()
            while len(reply) <= MAX_REPLY_BYTES:
                chunk = connection.recv(1)
                if not chunk:
                    break
                reply.extend(chunk)
                if chunk == b"\n":
                    break
    except socket.timeout as error:
        raise ProbeClientError("network probe timed out") from error
    except OSError as error:
        detail = str(error)
        if len(detail) > 160:
            detail = detail[:160]
        raise ProbeClientError("connection failed: " + detail) from error

    if not reply or reply[-1:] != b"\n" or len(reply) > MAX_REPLY_BYTES:
        raise ProbeClientError("server returned an incomplete or oversized reply")
    try:
        return bytes(reply[:-1]).decode("ascii")
    except UnicodeDecodeError as error:
        raise ProbeClientError("server reply was not ASCII") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("message")
    args = parser.parse_args(argv)
    try:
        response = exchange(args.host, args.port, args.message)
    except ProbeClientError as error:
        print("network probe client: %s" % error, file=sys.stderr)
        return 1
    print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
