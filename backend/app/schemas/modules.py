from pydantic import BaseModel, Field
from typing import List, Dict

# Q&A Module Schemas
class QAPostRequest(BaseModel):
    Question: str = Field(..., min_length=5, description="The question or concept to ask")

class QAPostResponse(BaseModel):
    Answer: str
    RelatedConcepts: List[str] = []
    AdditionalContext: str

# Explanation Module Schemas
class ExplainPostRequest(BaseModel):
    Topic: str = Field(..., min_length=2, description="The concept or topic to explain")

class ExplainPostResponse(BaseModel):
    Definition: str
    Examples: List[str] = []
    Applications: List[str] = []
    Summary: str

# Quiz Module Schemas
class QuizPostRequest(BaseModel):
    Topic: str = Field(..., min_length=2, description="The topic to generate a quiz for")
    Difficulty: str = Field("Medium", description="Difficulty level: Easy, Medium, Hard")
    QuestionCount: int = Field(5, ge=1, le=10, description="Number of questions (1-10)")

class QuizQuestion(BaseModel):
    QuestionText: str
    OptionA: str
    OptionB: str
    OptionC: str
    OptionD: str
    CorrectOption: str = Field(..., description="A, B, C, or D")
    Explanation: str

class QuizPostResponse(BaseModel):
    Quizzes: List[QuizQuestion]

# Summary Module Schemas
class SummaryPostRequest(BaseModel):
    Notes: str | None = Field(None, description="The raw study notes/content to summarize")
    # For file uploads, we'll handle PDF text extraction in the route, but this schema can receive raw text.

class SummaryPostResponse(BaseModel):
    Summary: str
    ImportantPoints: List[str] = []
    Formulas: List[str] = []
    Definitions: List[str] = []
    ExamNotes: str

# Learning Path Module Schemas
class LearnPostRequest(BaseModel):
    SkillName: str = Field(..., min_length=2, description="The skill name to generate roadmaps for")

class RoadmapDetail(BaseModel):
    Topics: List[str] = []
    Projects: List[str] = []
    Certifications: List[str] = []
    Resources: List[str] = []
    Timeline: str

class LearnPostResponse(BaseModel):
    Topic: str
    Level: str
    Beginner: RoadmapDetail
    Intermediate: RoadmapDetail
    Advanced: RoadmapDetail
    CareerSuggestions: List[str] = []
