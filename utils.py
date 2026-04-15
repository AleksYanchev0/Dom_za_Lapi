import jwt 
import datetime
from config import Config
from flask_mail import Message, Mail


mail = Mail()

def create_reset_token(email):
    payload = {
        "email":email,
        "exp": datetime.datetime.now() + datetime.timedelta(minutes=30)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

def validate_reset_token(token):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload["email"]
    
    except jwt.ExpiredSignatureError:
        return None
    
    except jwt.InvalidTokenError:
        return None
    
def send_email(email, token):
    reset_url = f"http://localhost:5001/new_password?token={token}"
    msg = Message(
        subject= "Password reset",
        sender=Config.MAIL_USERNAME,
        recipients=[email],
        body=f"Click the link to reset your password:\n\n{reset_url}\n\nExpires in 30 minutes.\n\nIf you didn't request this, ignore this email."
    )
    mail.send(msg)

