from flask import  request
from flask_restx import Resource, fields
from . import app, db, mail, api, bcrypt
from myapp.models import User, Organization
from myapp.schema import user_schema, users_schema, organization_schema, organizations_schema
from flask_mail import Message
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token



# Define Data Transfer Object for organization request
user_login = api.model("UserLogin", {
        "email": fields.String(required=True),
        "password": fields.String(required=True),
    })

# DEfine DTO for user registration
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

# Define DTO for organization login
organization_login = api.model("OrganizationLogin", {
    "email": fields.String(required=True),
    "password": fields.String(required=True),
})

password_reset = api.model('PasswordReset', {
        "password": fields.String(required=True)
    })

# Define a route for user registration
@api.route("/user/register")
class UserRegistration(Resource):
    @api.expect(user_registration,  validate = True)
    def post(self):
        """Submit user registration details"""
        data = request.get_json()
        user = user_schema.load(data)

        if not user.get("username") or not user.get("email") or not user.get("password") or not user.get("role"):
            return {"message": "All fields are required"}, 400

        existing_email = User.query.filter_by(email=user.get("email")).first()
        existing_username = User.query.filter_by(username=user.get("username")).first()
        if existing_email:
            return {"message": "Email already registered"}, 409
        if existing_username:
            return {"message": "Username already registered"}, 409
        
        new_user = User(**user)

        db.session.add(new_user)
        db.session.commit()

        return {"message": "User registered successfully!"}, 201

# Define a route for user login
@api.route("/user/login")
class UserLogin(Resource):
    @api.expect(user_login, validate=True)
    def post(self):
        """User login"""
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

# Define the OrganizationRequest resource
@api.route("/organization_requests")
class OrganizationRequestResource(Resource):
    @api.marshal_with(organization_request)
    def get(self):
        """Get a list of organization requests."""
    
        requests = Organization.query.filter_by(status=False).all()
    
        if not requests:
            api.abort(404, "No pending organization requests found!")
       
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


# Define a route for viewing and managing a specific organization request
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

# Define a route for organization login
@api.route("/organization/login")
class OrganizationLogin(Resource):
    @api.expect(organization_login, validate=True)
    def post(self):
        """Organization login"""
        data = request.get_json()
        organization = Organization.query.filter_by(email=data['email']).first()
        if organization:
            if bcrypt.check_password_hash(organization.password, data['password']):
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
                    return {"message": "Organization is pending approval. Please wait for approval."}, 403
            else:
                return {"message": "Invalid credentials"}, 401
        else:
            return {"message": "Organization not found"}, 404
