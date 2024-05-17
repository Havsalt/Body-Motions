from typing import NamedTuple as _NamedTuple


class Landmark(_NamedTuple):
    x: float
    y: float
    z: float
    visibility: float


class LandmarkSequence(_NamedTuple):
    landmark: list[Landmark]


class SolutionResult(_NamedTuple):
    pose_landmarks: LandmarkSequence
    pose_world_landmarks: LandmarkSequence
    segmentation_mask: None
