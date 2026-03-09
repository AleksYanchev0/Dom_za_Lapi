from flask import Blueprint, render_template, request
from models import Animal, User, db, Shelter
from flask_jwt_extended import jwt_required, get_jwt_identity

animal_bp = Blueprint("animal", __name__)

@animal_bp.route("/animals", methods=["GET"])
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


@animal_bp.route("/animals/<int:animal_id>", methods=["GET"])
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


@animal_bp.route("/animals", methods=["POST"])
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


@animal_bp.route("/animals/add")
def add_animal_page():
    return render_template("add_animal.html")