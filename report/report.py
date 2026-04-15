from flask import render_template, Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Report, db

report_bp = Blueprint("report", __name__)

@report_bp.route("/reports", methods=["GET"])
@jwt_required(optional=True)
def get_reports():
    if request.args.get("view") == "html":
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id)) if user_id else None
        is_admin = user and user.role == "admin"
        reports = Report.query.order_by(Report.created_at.desc()).all() if is_admin else []
        return render_template("reports.html", reports=reports, is_admin=is_admin)

    # JSON path (keep as-is for API use)
    reports = Report.query.all()
    return {
        "success": True,
        "count": len(reports),
        "data": [
            {
                "id": r.id,
                "text": r.text,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
                "user_id": r.user_id
            }
            for r in reports
        ]
    }


@report_bp.route("/reports", methods=["POST"])
@jwt_required()
def create_report():
    data = request.get_json()
    user_id = get_jwt_identity()

    if not data or "text" not in data:
        return {"success": False, "error": "Missing required fields"}, 400

    report = Report(
        text=data["text"],
        user_id=int(user_id)
    )

    db.session.add(report)
    db.session.commit()

    return {
        "success": True,
        "data": {
            "id": report.id,
            "text": report.text,
            "status": report.status,
            "created_at": report.created_at.isoformat()
        }
    }, 201

@report_bp.route("/reports/<int:report_id>/status", methods=["PATCH"])
@jwt_required()
def update_report_status(report_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user or user.role != "admin":
        return {"success": False, "error": "Access denied"}, 403

    report = Report.query.get(report_id)
    if not report:
        return {"success": False, "error": "Report not found"}, 404

    data = request.get_json()
    status = data.get("status")
    if status not in ["pending", "reviewed", "resolved"]:
        return {"success": False, "error": "Invalid status"}, 400

    report.status = status
    db.session.commit()
    return {"success": True, "message": f"Status updated to {status}"}
