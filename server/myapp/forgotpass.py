from flask import Flask, request
from flask_restx import Resource, fields
from flask_mail import Message
from . import bcrypt, mail, api, app, db
import secrets
from datetime import datetime, timedelta
from myapp.models import User

reset_tokens = {}

# Define DTO for the "Forgot Password" request
forgot_password_request = api.model("ForgotPasswordRequest", {
    "email": fields.String(required=True),
})

# Define DTO for the password reset request
password_reset = api.model("PasswordReset", {
    "password": fields.String(required=True),
})

# Generate a unique reset token using secrets
def generate_reset_token():
    reset_token = secrets.token_urlsafe(32)
    return reset_token

# Send a password reset email
def send_reset_email(email, reset_url):
    msg = Message(
        "Password Reset",
        sender="noemaingi@gmail.com", 
        recipients=[email],
    )
    msg.body = f"Click the following link to reset your password: {reset_url}"
    mail.send(msg)

# Create a new resource for initiating the "Forgot Password" process
@api.route("/user/forgot_password_request")
class ForgotPasswordRequest(Resource):
    @api.expect(forgot_password_request, validate=True)
    def post(self):
        data = request.get_json()
        email = data.get("email")

        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "User not found"}, 404

        reset_token = generate_reset_token()
        reset_tokens[reset_token] = user.id

        reset_url = f"http://127.0.0.1:8000/user/reset_password/{reset_token}"

        send_reset_email(email, reset_url)

        return {"message": "Password reset email sent successfully"}, 200

# Create a new resource for resetting the user's password
@api.route("/user/reset_password/<string:reset_token>")
class ResetPassword(Resource):
    @api.expect(password_reset, validate=True)
    def put(self, reset_token):
        data = request.get_json()
        new_password = data.get("password")

        user_id = reset_tokens.get(reset_token)
        if not user_id:
            return {"message": "Invalid reset token"}, 400

        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        db.session.commit()

        del reset_tokens[reset_token]  # Remove the used reset token

        return {"message": "Password reset successful"}, 200

