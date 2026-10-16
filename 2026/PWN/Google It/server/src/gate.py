#!/usr/bin/env python3
"""Public TCP relay into the isolated Chrome target network."""

from __future__ import annotations

import os
import select
import socket
import threading
import time


UPSTREAM_HOST = os.environ.get("UPSTREAM_HOST", "target")
UPSTREAM_PORT = 1337
LISTEN_PORT = 1337
CONNECT_TIMEOUT = 10
IDLE_TIMEOUT = int(os.environ.get("GATE_IDLE_TIMEOUT_SECONDS", "420"))
MAX_BUFFER = 256 * 1024


def relay(client: socket.socket) -> None:
    try:
        upstream = socket.create_connection(
            (UPSTREAM_HOST, UPSTREAM_PORT), timeout=CONNECT_TIMEOUT
        )
    except OSError:
        client.close()
        return

    client.setblocking(False)
    upstream.setblocking(False)
    sockets = (client, upstream)
    peer = {client: upstream, upstream: client}
    readable = set(sockets)
    pending = {client: bytearray(), upstream: bytearray()}
    shutdown_after_drain: set[socket.socket] = set()
    last_activity = time.monotonic()
    try:
        while time.monotonic() - last_activity < IDLE_TIMEOUT:
            readers = [
                source
                for source in readable
                if len(pending[peer[source]]) < MAX_BUFFER
            ]
            writers = [destination for destination in sockets if pending[destination]]
            if not readers and not writers:
                return
            ready_read, ready_write, _ = select.select(
                readers, writers, [], 5
            )
            for source in ready_read:
                chunk = source.recv(65536)
                if not chunk:
                    readable.discard(source)
                    shutdown_after_drain.add(peer[source])
                    continue
                pending[peer[source]].extend(chunk)
                last_activity = time.monotonic()
            for destination in ready_write:
                sent = destination.send(pending[destination])
                if sent:
                    del pending[destination][:sent]
                    last_activity = time.monotonic()
                if not pending[destination] and destination in shutdown_after_drain:
                    try:
                        destination.shutdown(socket.SHUT_WR)
                    except OSError:
                        pass
                    shutdown_after_drain.discard(destination)
            if not readable and not any(pending.values()):
                return
    except OSError:
        return
    finally:
        client.close()
        upstream.close()


def main() -> None:
    if not 30 <= IDLE_TIMEOUT <= 1800:
        raise RuntimeError("GATE_IDLE_TIMEOUT_SECONDS must be between 30 and 1800")
    with socket.create_server(("0.0.0.0", LISTEN_PORT), reuse_port=True) as listener:
        while True:
            client, _ = listener.accept()
            threading.Thread(target=relay, args=(client,), daemon=True).start()


if __name__ == "__main__":
    main()
