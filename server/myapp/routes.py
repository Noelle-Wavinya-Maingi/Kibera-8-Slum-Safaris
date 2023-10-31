from flask import request
from flask_restx import Resource, fields
from . import app, db, mail, api, bcrypt
from myapp.models import User, Organization
from flask_mail import Message
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


# Define Data Transfer Object for organization request
user_login = api.model("UserLogin", {
        "email": fields.String(required=True),
        "password": fields.String(required=True),
    })


user_registration = api.model("UserRegistration", {
        "email": fields.String(required=True),
        "password": fields.String(required=True),
        "username": fields.String(required=True),
        "role": fields.String(required=True),
    })

# Define Data Transfer Object for organization request
organization_request = api.model(
    "OrganizationRequest",
    {
        "id": fields.Integer,
        "name": fields.String,
        "description": fields.String,
        "email": fields.String,
        "status": fields.String,
    },
)


@api.route("/user/register")
class UserRegistration(Resource):
    @api.expect(user_registration,  validate = True)
    def post(self):
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        if not username or not email or not password or not role:
            return {"message": "All fields are required"}, 400

        existing_email = User.query.filter_by(email=email).first()
        existing_username = User.query.filter_by(username=username).first()
        if existing_email:
            return {"message": "Email already registered"}, 409
        if existing_username:
            return {"message": "Username already registered"}, 409
        
        new_user = User(username=username, email=email, password=password, role=role)

        db.session.add(new_user)
        db.session.commit()

        return {"message": "User registered successfully!"}, 201

@api.route("/user/login")
class UserLogin(Resource):
    @api.expect(user_login, validate=True)
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()

        if user and bcrypt.check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=user.id)
            return {
                "access_token": access_token,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }, 200
        else:
            return {"message": "Invalid credentials"}, 401

    @jwt_required
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }

# Define the OrganizationRequest resource
@api.route("/organization_requests")
class OrganizationRequestResource(Resource):
    @api.marshal_with(organization_request)
    def get(self):
        """Get a list of organization requests."""
        requests = Organization.query.filter_by(status=False).all()
        return requests

    @api.expect(organization_request, validate=True)
    @api.marshal_with(organization_request)
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


@api.route("/organization_requests/<int:id>")
class OrganizationRequestDetailResource(Resource):
    @api.marshal_with(organization_request)
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
