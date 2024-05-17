from math import degrees as rad2deg

from websockets.sync.server import serve, ServerConnection, WebSocketServer

import networking
from detection import Detector


def handler(websocket: ServerConnection) -> None:
    detector = Detector(flip_image=True)
    while detector.is_active() and detector.poll() != detector.MISSING_FRAME:
        detector.update()
        a = detector.get_point(16)
        b = detector.get_point(12)
        detector.render()
        if a is None or b is None:
            continue
        websocket.send(str(a - b).encode("utf-8"))


def main() -> int:
    print("[Info] Launching server")

    host, port = networking.get_address()
    with serve(handler, host, port) as server:
        print(f"[Info] Running on {host}:{port}")
        server.serve_forever()

    print("[Info] Exited")
    return 0
