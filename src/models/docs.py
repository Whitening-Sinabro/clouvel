from pydantic import BaseModel
from datetime import datetime


class ScanRequest(BaseModel):
    path: str


class DocFile(BaseModel):
    name: str
    size: int
    modified_at: datetime
    extension: str


class ScanResponse(BaseModel):
    path: str
    total_files: int
    files: list[DocFile]


class RequiredDoc(BaseModel):
    type: str
    name: str
    description: str
    patterns: list[str]


class DetectedDoc(BaseModel):
    type: str
    file: DocFile
    confidence: float


class MissingDoc(BaseModel):
    type: str
    name: str
    description: str
    priority: str  # "critical" | "recommended" | "optional"


class AnalyzeResponse(BaseModel):
    path: str
    detected: list[DetectedDoc]
    missing: list[MissingDoc]
    coverage: float  # 0.0 ~ 1.0
    summary: str
