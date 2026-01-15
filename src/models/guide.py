from pydantic import BaseModel


class GuideStep(BaseModel):
    step: int
    title: str
    description: str
    example: str | None = None


class PRDGuide(BaseModel):
    title: str
    tagline: str
    steps: list[GuideStep]


class CheckItem(BaseModel):
    id: str
    check: str
    detail: str
    priority: str


class CheckCategory(BaseModel):
    name: str
    items: list[CheckItem]


class VerifyGuide(BaseModel):
    title: str
    tagline: str
    categories: list[CheckCategory]
