from flask import Flask, request, render_template
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from config import Config
from models import db, Animal, Shelter, Report, User
from auth.auth import auth_bp
from shelter.shelter import shelter_bp
from animals.animal import animal_bp
from report.report import report_bp
from admin.admin import admin_bp
from user.user import user_bp
from utils import mail


load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)
mail.init_app(app)
db.init_app(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(shelter_bp)
app.register_blueprint(animal_bp)
app.register_blueprint(report_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route("/")
def home():
    return render_template("home.html")



if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True,
        use_reloader=False
    )