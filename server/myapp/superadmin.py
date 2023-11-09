from flask import request
from flask_restx import Resource
from . import app, db, mail, api, bcrypt, user_ns
from myapp.models import User
from myapp.schema import (
    user_schema
)
from flask_mail import Message
from flask_jwt_extended import get_jwt_identity, jwt_required
import secrets
from myapp.routes import user_registration
 
@user_ns.route("/admin/register") 
class AdminRegistration(Resource):
    @jwt_required()
    @user_ns.expect(user_registration, validate=True)
    def post(self):
        """Submit admin registration details"""
        data = request.get_json()
        user = user_schema.load(data)

        current_user_id = get_jwt_identity()
        print(current_user_id)

        # Fetch the current user based on their ID using filter_by
        current_user = User.query.filter_by(id=current_user_id).first()

        if current_user is not None and current_user.role == "superadmin":
            if (
                not user.get("username")
                or not user.get("email")
                or not user.get("role")
            ):
                return {"message": "Username, email, and role are required fields"}, 400

            # Check if the email or username is already registered
            existing_email = User.query.filter_by(email=user.get("email")).first()
            existing_username = User.query.filter_by(username=user.get("username")).first()
            if existing_email:
                return {"message": "Email already registered"}, 409
            if existing_username:
                return {"message": "Username already registered"}, 409

            new_admin = User(**user)

            # Check if the superadmin provided a password for the new admin
            provided_password = data.get("password")

            # Generate a random temporary password if no password was provided
            if not provided_password:
                temp_password = secrets.token_urlsafe(8)
                # Hash the temporary password
                temp_password_hashed = bcrypt.generate_password_hash(temp_password).decode("utf-8")
                new_admin.password = temp_password_hashed
            else:
                # Use the provided password and hash it
                password_hashed = bcrypt.generate_password_hash(provided_password).decode("utf-8")
                new_admin.password = password_hashed

            # Save the new admin in the database
            db.session.add(new_admin)
            db.session.commit()

            # Send the admin their login credentials via email
            msg = Message(
                "Admin Registration Successful",
                sender="admin@gmail.com",
                recipients=[new_admin.email],
            )
            if not provided_password:
                msg.body = f"Your admin registration is successful. Here are your login credentials:\nEmail: {new_admin.email}\nTemporary Password: {temp_password}"
            else:
                msg.body = f"Your admin registration is successful. Here are your login credentials:\nEmail: {new_admin.email}\nPassword: {provided_password}"

            mail.send(msg)

            # Send the password to the superadmin's email
            superadmin_email = "superadmin@gmail.com"  
            msg = Message(
                "Admin Registration Details",
                sender="admin@gmail.com",
                recipients=[superadmin_email],
            )
            if not provided_password:
                msg.body = f"An admin has been registered. Here are their details:\nEmail: {new_admin.email}\nTemporary Password: {temp_password_hashed}"
            else:
                msg.body = f"An admin has been registered. Here are their details:\nEmail: {new_admin.email}\nPassword: {password_hashed}"
            mail.send(msg)

            return {"message": "Admin registered successfully!", "role": user.get("role")}, 201
        else:
            return {"message": "Access denied. Superadmin privileges required."}, 403