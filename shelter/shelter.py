from flask import Blueprint, render_template, request
from models import Shelter, db, Animal, User
from flask_jwt_extended import jwt_required, get_jwt_identity

shelter_bp = Blueprint("shelter", __name__)

@shelter_bp.route("/shelters", methods=["GET"])
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


@shelter_bp.route("/shelters/register", methods=["GET"])
def get_shelter_register():
    return render_template("shelter_registration.html")


@shelter_bp.route("/shelters/<int:shelter_id>", methods=["GET"])
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


@shelter_bp.route("/shelters", methods=["POST"])
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
        photo_url=data.get("photo_url"),
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


@shelter_bp.route("/shelters/<int:shelter_id>/approve", methods=["PATCH"])
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


@shelter_bp.route("/shelters/<int:shelter_id>/decline", methods=["PATCH"])
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