from flask import Flask, request, render_template
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from config import Config
from models import db, Animal, Shelter, Report, User


load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/shelters", methods=["GET"])
def get_shelters():
    query = Shelter.query.filter_by(is_approved=True)

    city = request.args.get("city")
    name = request.args.get("name")

    if city:
        query = query.filter(Shelter.city.ilike(f"%{city}%"))
    if name:
        query = query.filter(Shelter.name.ilike(f"%{name}%"))

    shelters = query.all()

    if request.args.get("view") == "html":
        return render_template("shelters.html", shelters=shelters)

    return {
        "success": True,
        "count": len(shelters),
        "data": [
            {
                "id": s.id,
                "name": s.name,
                "city": s.city,
                "phone": s.phone,
                "email": s.email,
                "photo_url": s.photo_url
            }
            for s in shelters
        ]
    }


@app.route("/shelters/register", methods=["GET"])
def get_shelter_register():
    return render_template("shelter_registration.html")


@app.route("/shelters/<int:shelter_id>", methods=["GET"])
def get_shelter(shelter_id):
    shelter = Shelter.query.get(shelter_id)

    if shelter is None:
        return {"success": False, "error": "Shelter not found"}, 404

    animals = Animal.query.filter_by(shelter_id=shelter.id).all()

    if request.args.get("view") == "html":
        return render_template("shelter_detail.html", shelter=shelter, animals=animals)

    return {
        "success": True,
        "data": {
            "id": shelter.id,
            "name": shelter.name,
            "city": shelter.city,
            "phone": shelter.phone,
            "email": shelter.email,
            "photo_url": shelter.photo_url,
            "animals": [
                {
                    "id": animal.id,
                    "name": animal.name,
                    "species": animal.species,
                    "breed": animal.breed,
                    "photo_url": animal.photo_url
                }
                for animal in animals
            ]
        }
    }


@app.route("/shelters", methods=["POST"])
def create_shelter():
    data = request.get_json()

    if not data:
        return {"success": False, "error": "Missing JSON body"}, 400

    required = ["name", "city", "email", "password", "username"]

    if not all(field in data and data[field].strip() for field in required):
        return {"success": False, "error": "Missing required fields"}, 400

    if User.query.filter_by(email=data["email"]).first():
        return {"success": False, "error": "Email already exists"}, 400

    user = User(email=data["email"], username=data["username"], role="shelter")
    user.set_password(data["password"])

    db.session.add(user)
    db.session.flush()

    shelter = Shelter(
        name=data["name"],
        city=data["city"],
        phone=data.get("phone"),
        email=data.get("email"),
        owner_id=user.id
    )
    db.session.add(shelter)
    db.session.commit()

    return {
        "success": True,
        "data": {
            "id": shelter.id,
            "name": shelter.name,
            "city": shelter.city
        }
    }, 201


@app.route("/animals", methods=["GET"])
def get_animals():
    query = Animal.query

    species = request.args.get("species")
    shelter_id = request.args.get("shelter_id")
    name = request.args.get("name")
    breed = request.args.get("breed")
    size = request.args.get("size")
    gender = request.args.get("gender")
    status = request.args.get("status")
    vaccinated = request.args.get("vaccinated")

    if species:
        query = query.filter(Animal.species.ilike(f"%{species}%"))
    if shelter_id:
        query = query.filter_by(shelter_id=shelter_id)
    if name:
        query = query.filter(Animal.name.ilike(f"%{name}%"))
    if breed:
        query = query.filter(Animal.breed.ilike(f"%{breed}%"))
    if size:
        query = query.filter_by(size=size)
    if gender:
        query = query.filter_by(gender=gender)
    if status:
        query = query.filter_by(status=status)
    if vaccinated is not None:
        query = query.filter_by(vaccinated=vaccinated == "true")

    animals = query.all()

    if request.args.get("view") == "html":
        return render_template("animals.html", animals=animals)

    return {
        "success": True,
        "count": len(animals),
        "data": [
            {
                "id": animal.id,
                "name": animal.name,
                "species": animal.species,
                "breed": animal.breed,
                "age": animal.age,
                "size": animal.size,
                "gender": animal.gender,
                "status": animal.status,
                "vaccinated": animal.vaccinated,
                "photo_url": animal.photo_url,
                "shelter_id": animal.shelter_id
            }
            for animal in animals
        ]
    }


@app.route("/animals/<int:animal_id>", methods=["GET"])
def get_animal(animal_id):
    animal = Animal.query.get(animal_id)

    if animal is None:
        return {"success": False, "error": "Animal not found"}, 404

    if request.args.get("view") == "html":
        return render_template("animal_detail.html", animal=animal)

    return {
        "success": True,
        "data": {
            "id": animal.id,
            "name": animal.name,
            "species": animal.species,
            "breed": animal.breed,
            "age": animal.age,
            "size": animal.size,
            "gender": animal.gender,
            "status": animal.status,
            "vaccinated": animal.vaccinated,
            "photo_url": animal.photo_url,
            "shelter_id": animal.shelter_id
        }
    }


@app.route("/animals", methods=["POST"])
@jwt_required()
def create_animal():
    data = request.get_json()
    user_id = get_jwt_identity()

    user = User.query.get(int(user_id))

    if not user:
        return {"success": False, "error": "User not found"}, 404

    if not data:
        return {"success": False, "error": "Missing JSON body"}, 400

    if user.role not in ["user", "shelter"]:
        return {"success": False, "error": "Not allowed to add animals"}, 403

    name = data.get("name")
    species = data.get("species")

    if not name or not species:
        return {"success": False, "error": "Missing required fields"}, 400

    shelter_id = None
    if user.role == "shelter":
        shelter = Shelter.query.filter_by(owner_id=user.id).first()
        if shelter:
            shelter_id = shelter.id

    animal = Animal(
        name=name,
        species=species,
        breed=data.get("breed"),
        age=data.get("age"),
        size=data.get("size"),
        gender=data.get("gender"),
        status=data.get("status", "available"),
        vaccinated=data.get("vaccinated", False),
        photo_url=data.get("photo_url"),
        shelter_id=shelter_id
    )

    db.session.add(animal)
    db.session.commit()

    return {
        "success": True,
        "data": {
            "id": animal.id,
            "name": animal.name,
            "species": animal.species,
            "breed": animal.breed,
            "shelter_id": animal.shelter_id
        }
    }, 201


@app.route("/animals/add")
def add_animal_page():
    return render_template("add_animal.html")


@app.route("/reports", methods=["GET"])
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


@app.route("/reports", methods=["POST"])
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

@app.route("/reports/<int:report_id>/status", methods=["PATCH"])
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


@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


@app.route("/auth/register", methods=["POST"])
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


@app.route("/auth/login", methods=["POST"])
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


@app.route("/shelters/<int:shelter_id>/approve", methods=["PATCH"])
@jwt_required()
def approve_shelter(shelter_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user or user.role != "admin":
        return {"success": False, "error": "Access denied"}, 403

    shelter = Shelter.query.get(shelter_id)

    if not shelter:
        return {"success": False, "error": "Shelter not found"}, 404

    shelter.is_approved = True
    db.session.commit()

    return {"success": True, "message": f"{shelter.name} approved"}


@app.route("/shelters/<int:shelter_id>/decline", methods=["PATCH"])
@jwt_required()
def decline_shelter(shelter_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user or user.role != "admin":
        return {"success": False, "error": "Access denied"}, 403

    shelter = Shelter.query.get(shelter_id)

    if not shelter:
        return {"success": False, "error": "Shelter not found"}, 404

    db.session.delete(shelter)
    db.session.commit()

    return {"success": True, "message": f"{shelter.name} declined and removed"}


@app.route("/admin/shelters", methods=["GET"])
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


@app.route("/admin")
def admin_page():
    return render_template("shelter_admin.html")


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True,
        use_reloader=False
    )