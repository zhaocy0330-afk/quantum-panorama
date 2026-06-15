from __future__ import annotations

import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def find_free_port(start: int = 8501, end: int = 8599) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free port found for Streamlit.")


def main() -> None:
    root = Path(__file__).resolve().parent
    port = find_free_port()
    url = f"http://localhost:{port}"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(root / "app.py"),
        "--server.headless",
        "true",
        "--server.port",
        str(port),
    ]
    process = subprocess.Popen(cmd, cwd=root)
    time.sleep(3)
    webbrowser.open(url)
    print(f"Quantum Panorama is running at {url}")
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()


if __name__ == "__main__":
    main()

