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
            data = conn.recv(4096)
            if data:
                try:
                    msg = json.loads(data.decode())
                    self._handle(msg, conn)
                except (json.JSONDecodeError, KeyError):
                    conn.sendall(json.dumps({"error": "invalid message"}).encode())
            conn.close()

    def _handle(self, msg: dict, conn: socket.socket) -> None:
        action = msg.get("action")
        if action == "recognize":
            audio = bytes.fromhex(msg.get("audio", ""))
            if self._recognizer:
                self._recognizer.feed(audio)
            conn.sendall(json.dumps({"status": "ok"}).encode())
        elif action == "result":
            if self._recognizer:
                text = self._recognizer.stop()
                conn.sendall(json.dumps({"text": text}).encode())
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
