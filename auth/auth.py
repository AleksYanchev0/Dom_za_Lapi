from flask import Blueprint, render_template, request
from flask_jwt_extended import create_access_token
from models import User, db
from utils import create_reset_token, validate_reset_token, send_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@auth_bp.route("/forgot_password", methods=["GET"])
def forgot_password_page():
    return render_template("send_email.html")

@auth_bp.route("/new_password", methods=["GET"])
def reset_password_page():
    token = request.args.get("token")
    if not token:
        return {"success": False, "error": "Invalid or expired token"}, 400
    return render_template("reset_password.html", token=token)

@auth_bp.route("/profile", methods=["GET"])
def profile_page():
    return render_template("profile.html")

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return {"success": False, "error": "Missing JSON body"}, 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not username or not email or not password:
        return {"success": False, "error": "Username, email and password are required"}, 400

    if User.query.filter(
        (User.username == username) | (User.email == email)
    ).first():
        return {"success": False, "error": "Username or email already exists"}, 409

    user = User(username=username, email=email, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return {"success": True, "message": "User registered successfully"}, 201

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return {"success": False, "error": "Missing JSON body"}, 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"success": False, "error": "Email and password required"}, 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return {"success": False, "error": "Невалидни данни"}, 401

    access_token = create_access_token(identity=str(user.id))

    return {
        "success": True,
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }

@auth_bp.route("/auth/forgot_password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    if not data:
        return {"success": False, "error": "Missing JSON body"}, 400

    email = data.get("email")
    if not email:
        return {"success": False, "error": "Email is required"}, 400

    user = User.query.filter_by(email=email).first()
    if user:
        token = create_reset_token(email)
        send_email(email, token)

    return {"success": True, "message": "If that email exists, a reset link was sent"}, 200

@auth_bp.route("/auth/reset_password", methods=["POST"])
def reset_password():
    data = request.get_json()
    if not data:
        return {"success": False, "error": "Missing JSON body"}, 400

    password = data.get("password")
    token = data.get("token")

    if not token or not password:
        return {"success": False, "error": "Password and token required"}, 400

    email = validate_reset_token(token)
    if not email:
        return {"success": False, "error": "Invalid or expired token"}, 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return {"success": False, "error": "User not found"}, 404

    user.set_password(password)
    db.session.commit()

    return {"success": True, "message": "Password updated successfully"}, 200