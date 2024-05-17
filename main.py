print("[Info] Loading modules")

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
from typing import NamedTuple
from math import degrees as rad2deg
import cv2
import mediapipe as mp
import mediapipe.python.solutions.pose as mp_pose
import mediapipe.python.solutions.drawing_utils as mp_drawing
import pygame
from linflex import Vec2, Vec2i


class Landmark(NamedTuple):
    x: float
    y: float
    z: float
    visibility: float


class LandmarkSequence(NamedTuple):
    landmark: list[Landmark]


class SolutionResult(NamedTuple):
    pose_landmarks: LandmarkSequence
    pose_world_landmarks: LandmarkSequence
    segmentation_mask: None


def read_position(frame, landmarks: LandmarkSequence, index: int) -> Vec2i:
    landmark = landmarks.landmark[index]
    height, width, _ = frame.shape
    x, y = int(landmark.x * width), int(landmark.y * height)
    return Vec2i(x, y)


CAMERA = 0
MISSING_FRAME = 0
HORIZONTAL = 1
FPS = 60
BLACK = (0, 0, 0)
SCREEN_SIZE = (
    500,
    300
)


def main() -> int:
    print("[Info] Started")

    stream = cv2.VideoCapture(CAMERA)
    model = mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    screen = pygame.display.set_mode(SCREEN_SIZE, flags=pygame.RESIZABLE)
    clock = pygame.time.Clock()

    while stream.isOpened():
        return_code, frame = stream.read()
        if return_code == MISSING_FRAME:
            stream.release()
            print("[Error] Missing frame")
            return 1 # missing frame
        frame_flipped = cv2.flip(frame, HORIZONTAL)
        # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)

        # process the image to detect hands
        results = model.process(frame_rgb) # type: SolutionResult  # type: ignore
        if not results.pose_landmarks:
            continue
        # draw the pose landmarks on the image
        mp_drawing.draw_landmarks(
            frame_flipped,
            results.pose_landmarks,
            connections=list(mp_pose.POSE_CONNECTIONS)
            )
        a = read_position(frame, results.pose_landmarks, 14)
        b = read_position(frame, results.pose_landmarks, 16)
        c = read_position(frame, results.pose_landmarks, 15)
        length = a.distance_to(b)
        relative = b - a
        angle = a.angle_to(b)
        print("", relative, rad2deg(angle), end="\r")

        # render section
        screen.fill(BLACK)
        # render world
        pygame.draw.rect(screen, pygame.Color("RED"), (b.to_tuple(), (50, 50)))
        pygame.draw.rect(screen, pygame.Color("RED"), (c.to_tuple(), (50, 50)))
        # update display
        pygame.display.flip()
        clock.tick(FPS)
        
        cv2.imshow("Test", frame_flipped)
        cv2.waitKey(1)
    
    # exit
    print("[Info] Exited")
    return 0
