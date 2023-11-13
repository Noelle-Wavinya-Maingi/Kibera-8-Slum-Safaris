from flask import request, url_for
from flask_restx import Resource, fields
from . import app, db, mail, api, bcrypt, user_ns, organization_ns
from myapp.models import User, Organization
from myapp.schema import (
    user_schema,
    users_schema,
    organization_schema,
    organizations_schema,
)
from flask_mail import Message
from flask_jwt_extended import create_access_token
import secrets

# Define Data Transfer Object for organization request
user_login = user_ns.model(
    "UserLogin",
    {
        "email": fields.String(required=True),
        "password": fields.String(required=True),
    },
)

# Define DTO for user registration
user_registration = user_ns.model(
    "UserRegistration",
    {
        "email": fields.String(required=True),
        "password": fields.String(required=True),
        "username": fields.String(required=True),
        "role": fields.String(required=True),
    },
)

# Define Data Transfer Object for organization request
organization_request = organization_ns.model(
    "OrganizationRequest",
    {
        "id": fields.Integer,
        "name": fields.String,
        "description": fields.String,
        "email": fields.String,
        "status": fields.String,
    },
)

# Define DTO for organization login
organization_login = organization_ns.model(
    "OrganizationLogin",
    {
        "email": fields.String(required=True),
        "password": fields.String(required=True),
    },
)

password_reset = user_ns.model("PasswordReset", {"password": fields.String(required=True)})


@user_ns.route("/register")
class UserRegistration(Resource):
    @user_ns.expect(user_registration, validate=True)
    def post(self):
        """Submit user registration details"""
        data = request.get_json()
        loaded_user_data = user_schema.load(data)

        if (
            not loaded_user_data.get("username")
            or not loaded_user_data.get("email")
            or not loaded_user_data.get("password")
            or not loaded_user_data.get("role")
        ):
            return {"message": "All fields are required"}, 400

        existing_email = User.query.filter_by(email=loaded_user_data.get("email")).first()
        existing_username = User.query.filter_by(username=loaded_user_data.get("username")).first()
        if existing_email:
            return {"message": "Email already registered"}, 409
        if existing_username:
            return {"message": "Username already registered"}, 409

        # Generate a verification token
        verification_token = generate_verification_token()

        # Create a new instance of the User model
        new_user = User(
            username=loaded_user_data["username"],
            email=loaded_user_data["email"],
            password=loaded_user_data["password"],
            role=loaded_user_data["role"],
            verification_token=verification_token,
        )

        db.session.add(new_user)
        db.session.commit()

        # Send a verification email
        verification_link = f"http://127.0.0.1:8000/User/verify/{verification_token}"
        msg = Message(
            "Verify Your Email",
            sender="noellemaingi@gmail.com",
            recipients=[new_user.email],
        )
        msg.body = f"Click the following link to verify your email: {verification_link}"
        mail.send(msg)

        return {"message": "User registered successfully! Check your email for verification."}, 201

def generate_verification_token():
    """
    Generate a secure verification token.
    """
    return secrets.token_urlsafe(30)

@user_ns.route("/verify/<token>")
class UserVerification(Resource):
    def get(self, token):
        """Verify user email using the provided token."""
        user = User.query.filter_by(verification_token=token).first()

        if user:
            # Mark the user as verified
            user.verification_token = None
            db.session.commit()
            return {"message": "Email verified successfully!"}, 200
        else:
            return {"message": "Invalid verification token"}, 400


@user_ns.route("/login")
class UserLogin(Resource):
    @user_ns.expect(user_login, validate=True)
    def post(self):
        """User login"""
        data = request.get_json()
        user = User.query.filter_by(email=data["email"]).first()

        if user and bcrypt.check_password_hash(user.password, data["password"]):
            if user.verification_token is None:  
                role = user.role
                access_token = create_access_token(identity=user.id)
                return {
                    "access_token": access_token,
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": role,
                }, 200
            else:
                return {"message": "Email not verified. Please verify your email first."}, 401
        else:
            return {"message": "Invalid credentials"}, 401

# Define the OrganizationRequest resource
@organization_ns.route("/requests")
class OrganizationRequestResource(Resource):
    @organization_ns.marshal_with(organization_request)
    def get(self):
        """Get a list of organization requests."""
        requests = Organization.query.filter_by(status=False).all()

        if not requests:
            api.abort(404, "No pending organization requests found!")

        return requests

    @organization_ns.expect(organization_request, validate=True)
    @organization_ns.marshal_with(organization_request)
    def post(self):
        """Submit an organization request."""
        data = request.get_json()
        print(data)
        organization = Organization(**data)

        # Save the organization request in the database
        db.session.add(organization)
        db.session.commit()

        # Send an email to the admin
        admin_email = "noemaingi@gmail.com"
        msg = Message(
            "New Organization Request",
            sender="noellemaingi@gmail.com",
            recipients=[admin_email],
        )
        msg.body = f"New organization request: {organization.name}"
        mail.send(msg)

        return organization, 201


@organization_ns.route("/requests/<int:id>")
class OrganizationRequestDetailResource(Resource):
    @organization_ns.marshal_with(organization_request)
    def get(self, id):
        """Get details of an organization request by ID."""
        organization = Organization.query.get(id)
        if organization is None:
            api.abort(404, "Organization request not found")
        return organization

    def put(self, id):
        """Approve or reject an organization request."""
        organization = Organization.query.get(id)
        if organization is None:
            api.abort(404, "Organization request not found")

        data = request.get_json()
        status = data.get("status")
        if status not in ("approved", "rejected"):
            api.abort(400, "Invalid status")

        if status == "approved":
            organization.approve_request()

            # Send the organization a password
            temp_password = organization.generate_temp_password()
            organization.send_password_email(temp_password)

        if status == "rejected":
            reason = data.get("reason")
            if not reason:
                api.abort(400, "Reason is required for rejection")
            organization.reject_request(reason)

        return {"message": f"Organization request {id} has been {status}"}


@organization_ns.route("/login")
class OrganizationLogin(Resource):
    @organization_ns.expect(organization_login, validate=True)
    def post(self):
        """Organization login"""
        data = request.get_json()
        organization = Organization.query.filter_by(email=data["email"]).first()
        if organization:
            if bcrypt.check_password_hash(organization.password, data["password"]):
                if organization.status:
                    access_token = create_access_token(identity=organization.id)
                    return {
                        "access_token": access_token,
                        "organization_id": organization.id,
                        "name": organization.name,
                        "email": organization.email,
                        "status": organization.status,
                    }, 200
                else:
                    return {
                        "message": "Organization is pending approval. Please wait for approval."
                    }, 403
            else:
                return {"message": "Invalid credentials"}, 401
        else:
            return {"message": "Organization not found"}, 404
