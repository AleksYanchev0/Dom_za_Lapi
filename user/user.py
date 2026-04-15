from flask import Blueprint, request, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, db

user_bp = Blueprint("user", __name__)

@user_bp.route("/users/me", methods=["GET"])
@jwt_required()  # ← fixed
def get_user_info():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return {"success": False, "error": "User not found"}, 404

    return {
        "success": True,
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "role": user.role
        }
    }, 200

@user_bp.route("/users/me", methods=["PATCH"])
@jwt_required()  # ← fixed
def update_user_info():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return {"success": False, "error": "User not found"}, 404

    data = request.get_json()

    if not data:
        return {"success": False, "error": "Missing JSON body"}, 400

    # check if new email already taken
    new_email = data.get("email")
    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            return {"success": False, "error": "Email already in use"}, 409

    # check if new username already taken
    new_username = data.get("username")
    if new_username and new_username != user.username:
        if User.query.filter_by(username=new_username).first():
            return {"success": False, "error": "Username already in use"}, 409

    if new_username:
        user.username = new_username
    if new_email:
        user.email = new_email
    if data.get("phone"):
        user.phone = data.get("phone")

    db.session.commit()

    return {"success": True, "message": "Profile updated"}, 200

@user_bp.route("/users/me/password", methods=["PATCH"])
@jwt_required()
def change_user_password():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return {"success": False, "error": "User doesn't exist"}, 404

    current_password = request.json.get("current_password")
    new_password = request.json.get("new_password")

    if not current_password or not new_password:
        return {"success": False, "error": "Both fields are required"}, 400

    if not user.check_password(current_password):
        return {"success": False, "error": "Invalid password"}, 401

    if current_password == new_password:
        return {"success": False, "error": "New password must be different"}, 400

    user.set_password(new_password)
    db.session.commit()

    return {"success": True, "message": "Password updated successfully"}, 200

@user_bp.route("/users/me", methods=["DELETE"])
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return {"success": False, "error": "User doesn't exist"}, 404

    db.session.delete(user)
    db.session.commit()

    return {"success": True, "message": "Account deleted"}, 200

@user_bp.route("/user_info", methods=["GET"])
def user_info_page():
    return render_template("user_info.html")