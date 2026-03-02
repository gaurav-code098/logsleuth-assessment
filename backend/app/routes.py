from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LogAnalysis
from app.schemas import LogSubmissionRequest
from app.services.groq_service import analyze_log_with_groq

router = APIRouter()

@router.get("/logs")
def get_logs(x_session_id: str = Header(...), db: Session = Depends(get_db)):
    """Fetch logs strictly for the current anonymous session."""
    logs = db.query(LogAnalysis).filter(LogAnalysis.session_id == x_session_id).order_by(LogAnalysis.created_at.desc()).all()
    return logs

@router.post("/logs")
def submit_log(request: LogSubmissionRequest, x_session_id: str = Header(...), db: Session = Depends(get_db)):
    """Process a new log and tie it to the user's session ID."""
    # 1. Save the initial state with the session ID
    new_log = LogAnalysis(
        raw_log=request.raw_log, 
        status="pending",
        session_id=x_session_id  # <-- Tie it to the session
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    # 2. Call Groq
    try:
        ai_result = analyze_log_with_groq(request.raw_log)
        
        # 3. Update database on success
        new_log.status = "success"
        new_log.severity = ai_result.severity
        new_log.root_cause = ai_result.root_cause
        new_log.suggested_fix = ai_result.suggested_fix
        
    except Exception as e:
        # 4. Handle failure safely
        new_log.status = "failed"
        new_log.root_cause = str(e)
        
    db.commit()
    db.refresh(new_log)
    return new_log