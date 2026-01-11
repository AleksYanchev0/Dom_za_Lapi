from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(40), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    role = db.Column(db.String(20), default = "user")
    
class Shelter(db.Model):
    __tablename__ = "shelters"
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), nullable = False)
    city = db.Column(db.String(30), nullable = False)
    
class Animal(db.Model):
    __tablename__ = "animals"
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(40))
    species = db.Column(db.String(50), nullable=False)
    
    shelter_id = db.Column(db.Integer, db.ForeignKey("shelters.id"))
