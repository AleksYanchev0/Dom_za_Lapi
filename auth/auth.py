from flask import Blueprint, render_template, request
from flask_jwt_extended import create_access_token
from models import User, db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


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