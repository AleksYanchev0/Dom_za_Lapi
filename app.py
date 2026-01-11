from flask import Flask, request
from dotenv import load_dotenv
from config import Config
from sqlalchemy import text
from models import Animal, Shelter, db
import os


load_dotenv()


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route("/")
def home():
    return "Dom za Lapi is running"

@app.route("/db-test")
def db_test():
    db.session.execute(text("SELECT 1"))
    return "Database works!"

@app.route("/animals", methods = ["GET"])
def get_animals():
    animals = Animal.query.all()
    
    result = []
    for animal in animals:
        result.append({
            "id": animal.id,
            "name": animal.name,
            "species": animal.species,
            "shelter_id": animal.shelter.id
        })
        
    return {
        "success": True,
        "count": len(result),
        "data": result
    }
    
@app.route("/animals/<int:animal_id>", methods = ["GET"])
def get_animal(animal_id):
    animal = Animal.query.get(animal_id)
    
    if animal is None:
        return {
            "success": False,
            "error": "Animal not found!"
        }, 404
        
    return {
        "success": True,
        "data": {
            "id": animal.id,
            "name": animal.name,
            "species": animal.species,
            "shelter_id": animal.shelter_id
        }
    }
    
@app.route("/animals", methods = ["POST"])
def create_animal():
    
    data = request.get_json()
    
    if not data:
        return {
            "success": False,
            "error": "Missing JSON body"
        }, 400
        
    if "name" not in data or "species" not in data or "shelter_id" not in data:
        return {
            "success": False,
            "error": "Missing required fields"
        }, 400
        
    animal = Animal(
        name = data["name"],
        species = data["species"],
        shelter_id = data["shelter_id"]
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
    
@app.route("/shelters", methods = ["POST"])
def create_shelter():
    
    data = request.get_json()
    
    if not data:
        return {
            "success": False,
            "error": "Missing JSON body"
        }, 400

    if "name" not in data or "city" not in data:
        return {
            "success": False,
            "error": "Missing required fields"
        }, 400
        
    shelter = Shelter(
        name = data["name"],
        city = data["city"]
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
    
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True,
        use_reloader=False
    )
