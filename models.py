from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default="user")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    reports = db.relationship('Report', backref='user', lazy=True, cascade="all, delete-orphan")
    animals = db.relationship('Animal', foreign_keys='Animal.user_id', backref='owner', lazy=True, cascade="all, delete-orphan")
    shelters = db.relationship('Shelter', foreign_keys='Shelter.owner_id', backref='owner', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Shelter(db.Model):
    __tablename__ = "shelters"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    
    animals = db.relationship("Animal", foreign_keys='Animal.shelter_id', backref="shelter", lazy=True, cascade="all, delete-orphan")


class Animal(db.Model):
    __tablename__ = "animals"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100), nullable=True)
    age = db.Column(db.String(20), nullable=True)        # puppy / young / adult / senior
    size = db.Column(db.String(20), nullable=True)       # small / medium / large
    gender = db.Column(db.String(10), nullable=True)     # male / female
    status = db.Column(db.String(30), default="available")  # available / adopted / in treatment
    vaccinated = db.Column(db.Boolean, default=False)
    photo_url = db.Column(db.String(500), nullable=True)
    
    shelter_id = db.Column(db.Integer, db.ForeignKey("shelters.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)


class Report(db.Model):
    __tablename__ = "reports"
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(50), default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)