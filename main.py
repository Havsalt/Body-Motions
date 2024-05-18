from websockets.sync.server import serve, ServerConnection
from linflex import Vec2

import networking
from detection import Detector



def handler(websocket: ServerConnection) -> None:
    print("[Info] Connection established")
    detector = Detector(
        flip_horizontal=True,
        flip_vertical=True,
        world_depth=500
    )
    while detector.is_active() and detector.poll() != detector.MISSING_FRAME:
        detector.update()
        right_shoulder = detector.get_point_3d(12)
        left_shoulder = detector.get_point_3d(11)
        if right_shoulder is not None and left_shoulder is not None:
            rel = right_shoulder - left_shoulder
            # websocket.send("X" + str(0))
            # websocket.send("Y" + str(rel.y))
            # websocket.send("Z" + str(Vec2(rel.x, rel.y).angle()))
            websocket.send("SHOULDER" + ",".join(map(str, rel.to_tuple())))

            right_hip = detector.get_point_3d(24)
            left_hip = detector.get_point_3d(23)
            if right_hip is not None and left_hip is not None:
                mid_hip = right_hip.lerp(left_hip, 0.50)
                mid_shoulder = right_shoulder.lerp(left_shoulder, 0.50)
                backbone = mid_shoulder - mid_hip
                turn_angle = Vec2(backbone.x, backbone.z).angle()
                local = backbone.rotate_around_z(turn_angle)
                angle = Vec2(local.x, local.y).angle()
                # print(" ", backbone, end="\r")
                # websocket.send("X" + str(deg2rad(backbone.z + 40)))
                websocket.send("BACKBONE" + ",".join(map(str, backbone.to_tuple())))
        
        # detector.debug_display()
    
    print("[Info] Connection closed")


def main() -> int:
    print("[Info] Launching server")

    host, port = networking.get_address(localhost=False)
    with serve(handler, host, port) as server:
        print(f"[Info] Running on {host}:{port}")
        server.serve_forever()

    print("[Info] Exited")
    return 0
