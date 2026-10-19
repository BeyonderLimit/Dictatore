from __future__ import annotations

import json
import os
import socket
import sys
import threading
from pathlib import Path

from dictatore.config import load_config
from dictatore.recognizer import Recognizer


SOCKET_PATH = Path.home() / ".local" / "share" / "dictatore" / "daemon.sock"


class Daemon:
    def __init__(self) -> None:
        self._recognizer: Recognizer | None = None
        self._server: socket.socket | None = None
        self._running = False

    def start(self) -> None:
        cfg, _ = load_config()
        model_name = cfg.get("MODEL", "en-us")
        models_dir = Path.home() / ".local" / "share" / "dictatore" / "models"
        model_path = models_dir / model_name
        self._recognizer = Recognizer(str(model_path))
        self._recognizer.start()

        SOCKET_PATH.parent.mkdir(parents=True, exist_ok=True)
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()

        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server.bind(str(SOCKET_PATH))
        self._server.listen(1)
        self._running = True

        while self._running:
            conn, _ = self._server.accept()
            try:
                msg = self._recv_json(conn)
                if msg is None:
                    conn.sendall(json.dumps({"error": "invalid message"}).encode())
                else:
                    self._handle(msg, conn)
            except OSError:
                # Client hung up mid-request (broken pipe / reset): a single
                # bad client must not take down the daemon.
                pass
            finally:
                conn.close()

    def _recv_json(self, conn: socket.socket) -> dict | None:
        """Read one newline-terminated JSON message. Large audio payloads are
        fine as long as they are a single line ending in '\n'. Returns None on
        disconnect, decode error, or oversized message."""
        MAX_MESSAGE = 10 * 1024 * 1024  # ~1.2 h of raw 16 kHz s16 mono (hex)
        buf = b""
        while b"\n" not in buf:
            chunk = conn.recv(65536)
            if not chunk:
                break
            buf += chunk
            if len(buf) > MAX_MESSAGE:
                return None
        line = buf.split(b"\n", 1)[0] if buf else b""
        if not line.strip():
            return None
        try:
            return json.loads(line.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def _handle(self, msg: dict, conn: socket.socket) -> None:
        action = msg.get("action")
        if action == "recognize":
            try:
                audio = bytes.fromhex(msg.get("audio", ""))
            except ValueError:
                conn.sendall(json.dumps({"error": "invalid audio hex"}).encode())
                return
            if self._recognizer:
                self._recognizer.feed(audio)
            conn.sendall(json.dumps({"status": "ok"}).encode())
        elif action == "result":
            if self._recognizer:
                text = self._recognizer.stop()
                # Restart so the daemon keeps serving requests; the model
                # itself stays loaded in memory.
                self._recognizer.start()
                conn.sendall(json.dumps({"text": text}).encode())
            else:
                conn.sendall(json.dumps({"error": "recognizer not started"}).encode())
        elif action == "quit":
            self._running = False
            conn.sendall(json.dumps({"status": "ok"}).encode())
        else:
            conn.sendall(json.dumps({"error": "unknown action"}).encode())

    def stop(self) -> None:
        self._running = False
        if self._server:
            self._server.close()
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()


def start_daemon() -> None:
    daemon = Daemon()
    daemon.start()


if __name__ == "__main__":
    start_daemon()
