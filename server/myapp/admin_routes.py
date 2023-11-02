
from flask import request
from flask_restx import Resource, fields
from . import db, api, bcrypt, mail
from myapp.models import Beneficiary, Donation, Organization
from flask_mail import Message
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

# Define Data Transfer Object for beneficiary request
beneficiary_request = api.model(
    "BeneficiaryRequest",
    {
        "name": fields.String(required=True),
        "age": fields.Integer,
        "gender": fields.String,
        "address": fields.String,
    },
)

# Define Data Transfer Object for donation request
donation_request = api.model(
    "DonationRequest",
    {
        "amount": fields.Float(required=True),
        "donor_id": fields.Integer(required=True),
        "organization_id": fields.Integer(required=True),
        "is_anonymous": fields.Boolean(default=False),
        "recurrence_interval": fields.String,
    },
)

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

# Define Data Transfer Object for admin action on organization request
admin_action = api.model(
    "AdminAction",
    {
        "status": fields.String(required=True, enum=["approved", "rejected"]),
        "reason": fields.String,  # Required when rejecting
    },
)

@api.route("/beneficiaries")
class BeneficiaryResource(Resource):
    @api.marshal_with(beneficiary_request)
    @jwt_required()
    def get(self):
        """Get a list of beneficiaries."""
        beneficiaries = Beneficiary.query.all()
        return beneficiaries

    @api.expect(beneficiary_request, validate=True)
    @api.marshal_with(beneficiary_request)
    @jwt_required()
    def post(self):
        """Submit a new beneficiary request."""
        data = request.get_json()
        beneficiary = Beneficiary(**data)

        # Save the beneficiary request in the database
        db.session.add(beneficiary)
        db.session.commit()

        return beneficiary, 201

@api.route("/beneficiaries/<int:id>")
class BeneficiaryDetailResource(Resource):
    @api.marshal_with(beneficiary_request)
    @jwt_required()
    def get(self, id):
        """Get details of a beneficiary by ID."""
        beneficiary = Beneficiary.query.get(id)
        if beneficiary is None:
            api.abort(404, "Beneficiary not found")
        return beneficiary

@api.route("/donations")
class DonationResource(Resource):
    @api.marshal_with(donation_request)
    @jwt_required()
    def get(self):
        """Get a list of donations."""
        donations = Donation.query.all()
        return donations

    @api.expect(donation_request, validate=True)
    @api.marshal_with(donation_request)
    @jwt_required()
    def post(self):
        """Submit a new donation."""
        data = request.get_json()
        donation = Donation(**data)

        # Save the donation in the database
        db.session.add(donation)
        db.session.commit()

        return donation, 201

@api.route("/donations/<int:id>")
class DonationDetailResource(Resource):
    @api.marshal_with(donation_request)
    @jwt_required()
    def get(self, id):
        """Get details of a donation by ID."""
        donation = Donation.query.get(id)
        if donation is None:
            api.abort(404, "Donation not found")
        return donation
