from flask import Flask, request, render_template
from flask_migrate import Migrate
from dotenv import load_dotenv
from sqlalchemy import text

from config import Config
from models import db, Animal, Shelter, Report

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def home():
    return "Dom za Lapi is running"


@app.route("/db-test")
def db_test():
    db.session.execute(text("SELECT 1"))
    return "Database works!"


@app.route("/shelters", methods=["GET"])
def get_shelters():
    shelters = Shelter.query.all()

    if request.args.get("view") == "html":
        return render_template(
            "shelters.html",
            shelters=shelters
        )

    result = []
    for shelter in shelters:
        result.append({
            "id": shelter.id,
            "name": shelter.name,
            "city": shelter.city
        })

    return {
        "success": True,
        "count": len(result),
        "data": result
    }


@app.route("/shelters/<int:shelter_id>", methods=["GET"])
def get_shelter(shelter_id):
    shelter = Shelter.query.get(shelter_id)

    if shelter is None:
        return {"success": False, "error": "Shelter not found"}, 404

    animals = Animal.query.filter_by(shelter_id=shelter.id).all()

    if request.args.get("view") == "html":
        return render_template(
            "shelter_detail.html",
            shelter=shelter,
            animals=animals
        )

    return {
        "success": True,
        "data": {
            "id": shelter.id,
            "name": shelter.name,
            "city": shelter.city,
            "animals": [
                {
                    "id": animal.id,
                    "name": animal.name,
                    "species": animal.species
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

    if "name" not in data or "city" not in data:
        return {"success": False, "error": "Missing required fields"}, 400

    shelter = Shelter(name=data["name"], city=data["city"])
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

    if species:
        query = query.filter_by(species=species)

    if shelter_id:
        query = query.filter_by(shelter_id=shelter_id)

    animals = query.all()

    if request.args.get("view") == "html":
        return render_template(
            "animals.html",
            animals=animals
        )

    return {
        "success": True,
        "count": len(animals),
        "data": [
            {
                "id": animal.id,
                "name": animal.name,
                "species": animal.species,
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
        return render_template(
            "animal_detail.html",
            animal=animal
        )

    return {
        "success": True,
        "data": {
            "id": animal.id,
            "name": animal.name,
            "species": animal.species,
            "shelter_id": animal.shelter_id
        }
    }


@app.route("/animals", methods=["POST"])
def create_animal():
    data = request.get_json()

    if not data:
        return {"success": False, "error": "Missing JSON body"}, 400

    required = ["name", "species", "shelter_id"]
    if not all(field in data for field in required):
        return {"success": False, "error": "Missing required fields"}, 400

    animal = Animal(
        name=data["name"],
        species=data["species"],
        shelter_id=data["shelter_id"]
    )

    db.session.add(animal)
    db.session.commit()

    return {
        "success": True,
        "data": {
            "id": animal.id,
            "name": animal.name,
            "species": animal.species,
            "shelter_id": animal.shelter_id
        }
    }, 201


@app.route("/reports", methods=["GET"])
def get_reports():
    reports = Report.query.all()

    if request.args.get("view") == "html":
        return render_template(
            "reports.html",
            reports=reports
        )

    return {
        "success": True,
        "count": len(reports),
        "data": [
            {
                "id": report.id,
                "text": report.text,
                "status": report.status,
                "created_at": report.created_at.isoformat(),
                "user_id": report.user_id
            }
            for report in reports
        ]
    }


@app.route("/reports", methods=["POST"])
def create_report():
    data = request.get_json()

    if not data:
        return {"success": False, "error": "Missing JSON body"}, 400

    if "text" not in data or "user_id" not in data:
        return {"success": False, "error": "Missing required fields"}, 400

    report = Report(
        text=data["text"],
        user_id=data["user_id"]
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


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True,
        use_reloader=False
    )
