from flask import render_template, Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import User, Shelter


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/shelters", methods=["GET"])
@jwt_required()
def admin_get_shelters():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user or user.role != "admin":
        return {"success": False, "error": "Access denied"}, 403

    shelters = Shelter.query.all()

    return {
        "success": True,
        "data": [
            {
                "id": shelter.id,
                "name": shelter.name,
                "city": shelter.city,
                "is_approved": shelter.is_approved
            }
            for shelter in shelters
        ]
    }


@admin_bp.route("/admin")
def admin_page():
    return render_template("shelter_admin.html")