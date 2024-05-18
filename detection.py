print("[Info] Started loading modules")

from contextlib import redirect_stdout as _redirect_stdout

import cv2 as _cv2
import mediapipe.python.solutions.pose as _mp_pose
import mediapipe.python.solutions.drawing_utils as _mp_drawing
from linflex import Vec2 as _Vec2, Vec3 as _Vec3

from annotations import SolutionResult as _SolutionResult

print("[Info] Finished loading modules")


class Detector:
    CAMERA = 0
    MISSING_FRAME = 0
    HORIZONTAL = 1
    VERTICAL = 0
    _last_raw_frame: _cv2.typing.MatLike
    _last_frame: _cv2.typing.MatLike
    _last_results: _SolutionResult

    def __init__(
        self,
        flip_horizontal: bool = False,
        flip_vertical: bool = False,
        world_depth: float = 0
    ) -> None:
        self.flip_horizontal = flip_horizontal
        self.flip_vertical = flip_vertical
        self.world_depth = world_depth
        self._stream = _cv2.VideoCapture(Detector.CAMERA)
        self._model = _mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.poll() # initializes `self._last_frame`
    
    def is_active(self) -> bool:
        return self._stream.isOpened()

    def poll(self) -> int:
        return_code, frame = self._stream.read()
        if return_code != Detector.MISSING_FRAME:
            self._last_raw_frame = frame
        return return_code

    def stop(self) -> None:
        self._stream.release()
    
    def update(self) -> None:
        frame = self._last_raw_frame
        if self.flip_horizontal:
            frame = _cv2.flip(frame, Detector.HORIZONTAL)
        if self.flip_vertical:
            frame = _cv2.flip(frame, Detector.VERTICAL)
        self._last_frame = _cv2.cvtColor(frame, _cv2.COLOR_BGR2RGB)
        self._last_results = self._model.process(self._last_frame) # type: _SolutionResult  # type: ignore
    
    def get_point_2d(self, index: int) -> _Vec2 | None:
        if self._last_results.pose_landmarks:
            landmark = self._last_results.pose_landmarks.landmark[index]
            height, width, _ = self._last_frame.shape
            return _Vec2(
                landmark.x * width,
                landmark.y * height
            )
        return None
    
    def get_point_3d(self, index: int) -> _Vec3 | None:
        if self._last_results.pose_world_landmarks:
            landmark = self._last_results.pose_world_landmarks.landmark[index]
            height, width, _ = self._last_frame.shape
            return _Vec3(
                landmark.x * width,
                landmark.y * height,
                landmark.z * self.world_depth
            )
        return None

    def debug_display(self) -> None:
        if not self._last_results.pose_landmarks:
            return
        # draw the pose landmarks on the image
        surface = _cv2.cvtColor(self._last_frame, _cv2.COLOR_RGB2BGR)
        _mp_drawing.draw_landmarks(
            surface,
            self._last_results.pose_landmarks,
            connections=list(_mp_pose.POSE_CONNECTIONS)
            )
        _cv2.imshow("Debug Display", surface)
        _cv2.waitKey(1)
