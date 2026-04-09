"""Pydantic models for API request/response types."""

from pydantic import BaseModel


class Landmark(BaseModel):
    id: int
    name: str
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0


class FrameData(BaseModel):
    frame_id: int
    filename: str
    phase: str
    landmarks: list[Landmark]
    metrics: dict


class SessionData(BaseModel):
    session_id: str
    frames: list[FrameData]


class LandmarkUpdate(BaseModel):
    landmarks: list[Landmark]


class VideoInfo(BaseModel):
    fps: float
    frame_count: int
    width: int
    height: int
    duration: float
