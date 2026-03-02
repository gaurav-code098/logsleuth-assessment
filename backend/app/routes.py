from flask import Blueprint, request, jsonify
from app.database import SessionLocal
from app.models import LogAnalysis
from app.schemas import LogSubmissionRequest
from app.services.groq_service import analyze_log_with_groq
from pydantic import ValidationError

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route("/logs", methods=["GET"])
def get_logs():
    x_session_id = request.headers.get("X-Session-ID")
    if not x_session_id:
        return jsonify({"detail": "Missing X-Session-ID header"}), 400

    db = SessionLocal()
    try:
        logs = db.query(LogAnalysis).filter(LogAnalysis.session_id == x_session_id).order_by(LogAnalysis.created_at.desc()).all()
        
        # Serialize SQLAlchemy objects to dictionaries for JSON response
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "raw_log": log.raw_log,
                "status": log.status,
                "severity": log.severity,
                "root_cause": log.root_cause,
                "suggested_fix": log.suggested_fix,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        return jsonify(result), 200
    finally:
        db.close()

@api_blueprint.route("/logs", methods=["POST"])
def submit_log():
    x_session_id = request.headers.get("X-Session-ID")
    if not x_session_id:
        return jsonify({"detail": "Missing X-Session-ID header"}), 400

    # 1. Strict input validation using Pydantic (Maintains Interface Safety)
    try:
        req_data = LogSubmissionRequest(**request.json)
    except ValidationError as e:
        return jsonify({"detail": str(e)}), 422
    except TypeError:
        return jsonify({"detail": "Invalid JSON payload"}), 400

    db = SessionLocal()
    try:
        # 2. Save the initial state with the session ID
        new_log = LogAnalysis(
            raw_log=req_data.raw_log, 
            status="pending",
            session_id=x_session_id
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        # 3. Call Groq
        try:
            ai_result = analyze_log_with_groq(req_data.raw_log)
            
            # 4. Update database on success
            new_log.status = "success"
            new_log.severity = ai_result.severity
            new_log.root_cause = ai_result.root_cause
            new_log.suggested_fix = ai_result.suggested_fix
            
        except Exception as e:
            # 5. Handle failure safely (Observability)
            new_log.status = "failed"
            new_log.root_cause = str(e)
            
        db.commit()
        db.refresh(new_log)

        # Return the updated log object
        return jsonify({
            "id": new_log.id,
            "raw_log": new_log.raw_log,
            "status": new_log.status,
            "severity": new_log.severity,
            "root_cause": new_log.root_cause,
            "suggested_fix": new_log.suggested_fix,
            "created_at": new_log.created_at.isoformat() if new_log.created_at else None
        }), 200
    finally:
        db.close()
