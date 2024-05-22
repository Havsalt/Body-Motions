from websockets.sync.server import serve, ServerConnection

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
            websocket.send("REL_SHOULDER" + ",".join(map(str, rel.to_tuple())))

            right_hip = detector.get_point_3d(24)
            left_hip = detector.get_point_3d(23)
            if right_hip is not None and left_hip is not None:
                mid_hip = right_hip.lerp(left_hip, 0.50)
                mid_shoulder = right_shoulder.lerp(left_shoulder, 0.50)
                backbone = mid_shoulder - mid_hip
                websocket.send("REL_BACKBONE" + ",".join(map(str, backbone.to_tuple())))
        
        right_wrist = detector.get_point_3d(16)
        right_lbow = detector.get_point_3d(14)
        if right_wrist is not None and right_lbow is not None:
            front_rarm = right_wrist - right_lbow
            websocket.send("REL_FRONT_RARM" + ",".join(map(str, front_rarm.to_tuple())))
        
        if right_shoulder is not None and right_lbow is not None:
            rarm_pos = right_lbow - right_shoulder
            websocket.send("POS_FRONT_RARM" + ",".join(map(str, rarm_pos.to_tuple())))
        
        left_wrist = detector.get_point_3d(15)
        left_lbow = detector.get_point_3d(13)
        if left_wrist is not None and left_lbow is not None:
            front_larm = left_wrist - left_lbow
            websocket.send("REL_FRONT_LARM" + ",".join(map(str, front_larm.to_tuple())))
        
        if left_shoulder is not None and left_lbow is not None:
            larm_pos = left_lbow - left_shoulder
            websocket.send("POS_FRONT_LARM" + ",".join(map(str, larm_pos.to_tuple())))
        
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
