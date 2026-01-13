from flask import Flask, request, render_template
from flask_migrate import Migrate
from dotenv import load_dotenv
from config import Config
from sqlalchemy import text
from models import Animal, Shelter, db, Report




load_dotenv()


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# migrate = Migrate(app, db)

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

@app.route("/shelters", methods = ["GET"])
def get_shelters():
    shelters = Shelter.query.all()
    
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

@app.route("/shelters/<int:shelter_id>", methods = ["GET"])
def get_shelter(shelter_id):
    shelter = Shelter.query.get(shelter_id)

    if shelter is None:
        return {
            "success": False,
            "error": "Shelter not found!"
        }, 404
    
    return {
        "success": True,
        "data": {
            "id": shelter.id,
            "name": shelter.name,
            "city": shelter.city
        }
    }, 200

@app.route("/reports", methods = ["GET"])
def get_reports():
    '''reports = Report.query.all()

    result = []
    for report in reports:
        result.append({
            "id": report.id,
            "text": report.text,
            "created_at": report.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": report.status,
            "user_id": report.user_id
        }) '''
    return render_template("templates/login.html")
    '''return {
        "success": True,
        "count": len(result),
        "data": result
    }
'''

@app.route("/reports", methods=["POST"])
def handle_report():
    data = request.get_json()

    if not data:
        return {"success": False, "error": "Missing JSON body"}, 400
    ''' if data["command"]=="login"):
        login()
    elif data["command"]=="register":
              register() '''

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
            "created_at": report.created_at  
        }
    }, 201


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True,
        use_reloader=False
    )
