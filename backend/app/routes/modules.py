from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import json
from typing import Dict, Any, List

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.query import UserQuery
from backend.app.models.response import AIResponse
from backend.app.models.quiz import Quiz as QuizModel
from backend.app.models.summary import Summary as SummaryModel
from backend.app.models.learning_path import LearningPath as LearningPathModel

from backend.app.schemas.modules import (
    QAPostRequest, QAPostResponse,
    ExplainPostRequest, ExplainPostResponse,
    QuizPostRequest, QuizPostResponse, QuizQuestion,
    SummaryPostRequest, SummaryPostResponse,
    LearnPostRequest, LearnPostResponse, RoadmapDetail
)
from backend.app.middleware.auth_middleware import get_current_user_api
from backend.app.services.gemini import ask_gemini_qa, generate_gemini_quiz, summarize_gemini_content, generate_gemini_learning_path
from backend.app.services.lamini import get_lamini_explanation
from backend.app.utils.pdf_parser import extract_text_from_pdf

router = APIRouter(prefix="/api/modules", tags=["Learning Modules"])

# =====================================================================
# Q&A MODULE
# =====================================================================
@router.post("/qa", response_model=QAPostResponse)
def ask_question(
    payload: QAPostRequest,
    current_user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db)
):
    # 1. Create UserQuery
    db_query = UserQuery(
        UserID=current_user.UserID,
        QueryType="qa",
        QueryText=payload.Question
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)

    # 2. Get Gemini Response
    ai_data = ask_gemini_qa(payload.Question)

    # 3. Store AIResponse
    db_response = AIResponse(
        QueryID=db_query.QueryID,
        ResponseText=json.dumps(ai_data),
        ModelUsed="Gemini 1.5 Pro"
    )
    db.add(db_response)
    db.commit()

    return QAPostResponse(
        Answer=ai_data.get("Answer", ""),
        RelatedConcepts=ai_data.get("RelatedConcepts", []),
        AdditionalContext=ai_data.get("AdditionalContext", "")
    )

# =====================================================================
# EXPLANATION MODULE
# =====================================================================
@router.post("/explain", response_model=ExplainPostResponse)
def explain_concept(
    payload: ExplainPostRequest,
    current_user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db)
):
    # 1. Create UserQuery
    db_query = UserQuery(
        UserID=current_user.UserID,
        QueryType="explain",
        QueryText=payload.Topic
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)

    # 2. Get LaMini Explanation
    ai_data = get_lamini_explanation(payload.Topic)

    # 3. Store AIResponse
    db_response = AIResponse(
        QueryID=db_query.QueryID,
        ResponseText=json.dumps(ai_data),
        ModelUsed=ai_data.get("ModelUsed", "LaMini-Flan-T5")
    )
    db.add(db_response)
    db.commit()

    return ExplainPostResponse(
        Definition=ai_data.get("Definition", ""),
        Examples=ai_data.get("Examples", []),
        Applications=ai_data.get("Applications", []),
        Summary=ai_data.get("Summary", "")
    )

# =====================================================================
# QUIZ MODULE
# =====================================================================
@router.post("/quiz", response_model=QuizPostResponse)
def generate_quiz(
    payload: QuizPostRequest,
    current_user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db)
):
    # 1. Create UserQuery
    query_text = f"Topic: {payload.Topic} | Difficulty: {payload.Difficulty} | Count: {payload.QuestionCount}"
    db_query = UserQuery(
        UserID=current_user.UserID,
        QueryType="quiz",
        QueryText=query_text
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)

    # 2. Get Gemini Quiz
    ai_data = generate_gemini_quiz(payload.Topic, payload.Difficulty, payload.QuestionCount)
    quizzes_list = ai_data.get("Quizzes", [])

    # 3. Store each Quiz Question & generic AIResponse
    for q in quizzes_list:
        db_quiz_question = QuizModel(
            QueryID=db_query.QueryID,
            QuestionText=q.get("QuestionText", ""),
            OptionA=q.get("OptionA", ""),
            OptionB=q.get("OptionB", ""),
            OptionC=q.get("OptionC", ""),
            OptionD=q.get("OptionD", ""),
            CorrectOption=q.get("CorrectOption", "A"),
            Explanation=q.get("Explanation", "")
        )
        db.add(db_quiz_question)
        
    db_response = AIResponse(
        QueryID=db_query.QueryID,
        ResponseText=json.dumps(ai_data),
        ModelUsed="Gemini 1.5 Pro"
    )
    db.add(db_response)
    db.commit()

    # Format output response schema
    out_quizzes = [
        QuizQuestion(
            QuestionText=q.get("QuestionText", ""),
            OptionA=q.get("OptionA", ""),
            OptionB=q.get("OptionB", ""),
            OptionC=q.get("OptionC", ""),
            OptionD=q.get("OptionD", ""),
            CorrectOption=q.get("CorrectOption", "A"),
            Explanation=q.get("Explanation", "")
        ) for q in quizzes_list
    ]

    return QuizPostResponse(Quizzes=out_quizzes)

# =====================================================================
# SUMMARY MODULE
# =====================================================================
@router.post("/summarize", response_model=SummaryPostResponse)
def summarize_text(
    payload: SummaryPostRequest,
    current_user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db)
):
    if not payload.Notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content field 'Notes' is empty."
        )

    # 1. Create UserQuery
    # Limit stored text preview in DB if notes are extremely long
    preview = payload.Notes[:200] + "..." if len(payload.Notes) > 200 else payload.Notes
    db_query = UserQuery(
        UserID=current_user.UserID,
        QueryType="summarize",
        QueryText=f"Text Summary: {preview}"
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)

    # 2. Get Gemini Summary
    ai_data = summarize_gemini_content(payload.Notes)

    # 3. Store Summary record & AIResponse
    db_summary = SummaryModel(
        QueryID=db_query.QueryID,
        OriginalText=payload.Notes,
        SummaryText=ai_data.get("Summary", ""),
        ModelUsed="Gemini 1.5 Pro"
    )
    db.add(db_summary)

    db_response = AIResponse(
        QueryID=db_query.QueryID,
        ResponseText=json.dumps(ai_data),
        ModelUsed="Gemini 1.5 Pro"
    )
    db.add(db_response)
    db.commit()

    return SummaryPostResponse(
        Summary=ai_data.get("Summary", ""),
        ImportantPoints=ai_data.get("ImportantPoints", []),
        Formulas=ai_data.get("Formulas", []),
        Definitions=ai_data.get("Definitions", []),
        ExamNotes=ai_data.get("ExamNotes", "")
    )

@router.post("/summarize/pdf", response_model=SummaryPostResponse)
async def summarize_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a PDF file."
        )
        
    try:
        # Read file bytes
        file_bytes = await file.read()
        extracted_text = extract_text_from_pdf(file_bytes)
        
        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract any readable text from the uploaded PDF."
            )
            
        # 1. Create UserQuery
        db_query = UserQuery(
            UserID=current_user.UserID,
            QueryType="summarize",
            QueryText=f"PDF Summary: {file.filename}"
        )
        db.add(db_query)
        db.commit()
        db.refresh(db_query)

        # 2. Get Gemini Summary
        ai_data = summarize_gemini_content(extracted_text)

        # 3. Store Summary record & AIResponse
        # Storing first 50,000 characters of PDF in DB to prevent overflow
        db_summary = SummaryModel(
            QueryID=db_query.QueryID,
            OriginalText=extracted_text[:50000],
            SummaryText=ai_data.get("Summary", ""),
            ModelUsed="Gemini 1.5 Pro"
        )
        db.add(db_summary)

        db_response = AIResponse(
            QueryID=db_query.QueryID,
            ResponseText=json.dumps(ai_data),
            ModelUsed="Gemini 1.5 Pro"
        )
        db.add(db_response)
        db.commit()

        return SummaryPostResponse(
            Summary=ai_data.get("Summary", ""),
            ImportantPoints=ai_data.get("ImportantPoints", []),
            Formulas=ai_data.get("Formulas", []),
            Definitions=ai_data.get("Definitions", []),
            ExamNotes=ai_data.get("ExamNotes", "")
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )

# =====================================================================
# LEARNING PATH MODULE
# =====================================================================
@router.post("/learn/recommendations", response_model=LearnPostResponse)
def get_recommendations(
    payload: LearnPostRequest,
    current_user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db)
):
    # 1. Create UserQuery
    db_query = UserQuery(
        UserID=current_user.UserID,
        QueryType="learn",
        QueryText=payload.SkillName
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)

    # 2. Get Gemini learning path
    ai_data = generate_gemini_learning_path(payload.SkillName)

    # 3. Store Learning Path record & AIResponse
    beg = ai_data.get("Beginner", {})
    inter = ai_data.get("Intermediate", {})
    adv = ai_data.get("Advanced", {})
    
    # Store recommended topics, projects, etc. as JSON in RecommendedTopics
    recs = {
        "CareerSuggestions": ai_data.get("CareerSuggestions", [])
    }
    
    db_path = LearningPathModel(
        QueryID=db_query.QueryID,
        Topic=payload.SkillName,
        Level="All",
        Beginner=json.dumps(beg),
        Intermediate=json.dumps(inter),
        Advanced=json.dumps(adv),
        RecommendedTopics=json.dumps(recs)
    )
    db.add(db_path)

    db_response = AIResponse(
        QueryID=db_query.QueryID,
        ResponseText=json.dumps(ai_data),
        ModelUsed="Gemini 1.5 Pro"
    )
    db.add(db_response)
    db.commit()

    return LearnPostResponse(
        Topic=payload.SkillName,
        Level="All",
        Beginner=RoadmapDetail(
            Topics=beg.get("Topics", []),
            Projects=beg.get("Projects", []),
            Certifications=beg.get("Certifications", []),
            Resources=beg.get("Resources", []),
            Timeline=beg.get("Timeline", "")
        ),
        Intermediate=RoadmapDetail(
            Topics=inter.get("Topics", []),
            Projects=inter.get("Projects", []),
            Certifications=inter.get("Certifications", []),
            Resources=inter.get("Resources", []),
            Timeline=inter.get("Timeline", "")
        ),
        Advanced=RoadmapDetail(
            Topics=adv.get("Topics", []),
            Projects=adv.get("Projects", []),
            Certifications=adv.get("Certifications", []),
            Resources=adv.get("Resources", []),
            Timeline=adv.get("Timeline", "")
        ),
        CareerSuggestions=ai_data.get("CareerSuggestions", [])
    )
