print("[Info] Started loading modules")

from contextlib import redirect_stdout as _redirect_stdout

import cv2 as _cv2
import mediapipe.python.solutions.pose as _mp_pose
import mediapipe.python.solutions.drawing_utils as _mp_drawing
from linflex import Vec2i as _Vec2i

from annotations import (
    LandmarkSequence as _LandmarkSequence,
    SolutionResult as _SolutionResult
)

print("[Info] Finished loading modules")


def read_position(
    frame: _cv2.typing.MatLike,
    landmarks: _LandmarkSequence,
    index: int
) -> _Vec2i:
    landmark = landmarks.landmark[index]
    height, width, _ = frame.shape
    x, y = int(landmark.x * width), int(landmark.y * height)
    return _Vec2i(x, y)


class Detector:
    CAMERA = 0
    MISSING_FRAME = 0
    HORIZONTAL = 1
    _last_raw_frame: _cv2.typing.MatLike
    _last_frame: _cv2.typing.MatLike
    _last_results: _SolutionResult

    def __init__(self, flip_image: bool = False) -> None:
        self.flip_image = flip_image
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
        if self.flip_image:
            frame_flipped = _cv2.flip(self._last_raw_frame, Detector.HORIZONTAL)
            self._last_frame = _cv2.cvtColor(frame_flipped, _cv2.COLOR_BGR2RGB)
        else:
            self._last_frame = _cv2.cvtColor(self._last_raw_frame, _cv2.COLOR_BGR2RGB)
        self._last_results = self._model.process(self._last_frame) # type: _SolutionResult  # type: ignore
    
    def get_point(self, index: int) -> _Vec2i | None:
        if self._last_results.pose_landmarks:
            return read_position(self._last_frame, self._last_results.pose_landmarks, index)
        return None

    def render(self) -> None:
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
