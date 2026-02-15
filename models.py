from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(40), unique = True, nullable = False)
    
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    role = db.Column(db.String(20), default = "user")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reports = db.relationship('Report', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Shelter(db.Model):
    __tablename__ = "shelters"
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), nullable = False)
    city = db.Column(db.String(30), nullable = False)
    
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    is_approved = db.Column(db.Boolean, default=False)
    
    animals = db.relationship("Animal", backref="shelter", lazy=True)
    
class Animal(db.Model):
    __tablename__ = "animals"
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(40))
    species = db.Column(db.String(50), nullable=False)
    
    shelter_id = db.Column(db.Integer, db.ForeignKey("shelters.id"))
    
    
class Report(db.Model):
    __tablename__ = "reports"
    
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(50), default='pending')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
