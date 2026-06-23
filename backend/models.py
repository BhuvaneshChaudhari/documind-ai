from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class SourceItem(BaseModel):
    text: str
    source_file: str
    score: float


class QuestionResponse(BaseModel):
    answer: str
    confidence_score: float
    sources: list[SourceItem]


class SearchRequest(BaseModel):
    query: str
