from flask import request
from flask_restx import Resource, fields
from . import db, api, bcrypt, mail, stripe, beneficiary_ns, donation_ns, organization_ns
from myapp.models import Beneficiary, Donation, Organization
from flask_mail import Message
from flask_jwt_extended import get_jwt_identity, jwt_required

# Define Data Transfer Object for beneficiary request
beneficiary_request = beneficiary_ns.model(
    "BeneficiaryRequest",
    {
        "name": fields.String(required=True),
        "age": fields.Integer,
        "gender": fields.String,
        "address": fields.String,
    },
)

# Define Data Transfer Object for donation request
donation_request = donation_ns.model(
    "DonationRequest",
    {
        "amount": fields.Float(required=True),
        # "donor_id": fields.Integer(required=True),
        "organization_name": fields.String(required=True),
        "is_anonymous": fields.Boolean(default=False),
        "recurrence_interval": fields.String,
    },
)

donation_response = donation_ns.model(
    "DonationResponse",
    {
        "amount": fields.Float(required=True),
        "donor_id": fields.Integer(required=True),
        "organization_id": fields.Integer(required=True),
        "is_anonymous": fields.Boolean(default=False),
        "recurrence_interval": fields.String,
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

# Define Data Transfer Object for admin action on organization request
admin_action = api.model(
    "AdminAction",
    {
        "status": fields.String(required=True, enum=["approved", "rejected"]),
        "reason": fields.String,  # Required when rejecting
    },
)

@beneficiary_ns.route("/")
class BeneficiaryResource(Resource):
    @beneficiary_ns.marshal_with(beneficiary_request)
    @jwt_required()
    def get(self):
        """Get a list of beneficiaries."""
        beneficiaries = Beneficiary.query.all()
        return beneficiaries

    @beneficiary_ns.expect(beneficiary_request, validate=True)
    @beneficiary_ns.marshal_with(beneficiary_request)
    @jwt_required()
    def post(self):
        """Submit a new beneficiary request."""
        data = request.get_json()
        beneficiary = Beneficiary(**data)

        # Save the beneficiary request in the database
        db.session.add(beneficiary)
        db.session.commit()

        return beneficiary, 201

@beneficiary_ns.route("/<int:id>")
class BeneficiaryDetailResource(Resource):
    @beneficiary_ns.marshal_with(beneficiary_request)
    @jwt_required()
    def get(self, id):
        """Get details of a beneficiary by ID."""
        beneficiary = Beneficiary.query.get(id)
        if beneficiary is None:
            api.abort(404, "Beneficiary not found")
        return beneficiary
    
@donation_ns.route("/create-payment-intent", methods=["POST"])
class CreatePaymentIntentResource(Resource):
    @jwt_required()
    def post(self):
        """Post payment intent to Stripe"""
        data = request.get_json()
        amount = data['amount'] 
        currency = "usd"  

        try:
            # Create a Payment Intent using the Stripe API
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount),  
                currency=currency,
            )

            # Return the client secret for the Payment Intent
            return {"client_secret": payment_intent.client_secret}

        except Exception as e:
            return {"error": str(e)}, 400


@donation_ns.route("/")
class DonationResource(Resource):
    @donation_ns.marshal_with(donation_response)
    @jwt_required()
    def get(self):
        """Get a list of donations."""
        donations = Donation.query.all()
        return donations

    @donation_ns.expect(donation_request, validate=True)
    @donation_ns.marshal_with(donation_response)
    @jwt_required()
    def post(self):
        """Post a donation to an organization"""
        data = request.get_json()

        # Get the donor_id from the JWT token
        donor_id = get_jwt_identity()

        amount = data['amount']
        organization_name = data['organization_name'] 
        is_anonymous = data['is_anonymous']

        try:
            # Look up the organization by organization_name and get its organization_id
            organization = Organization.query.filter_by(name=organization_name).first()
            if organization is None:
                return {"message": "Organization not found"}, 404

            # Create a new Donation with the donor_id and organization_id
            donation = Donation(
                amount=amount,
                donor_id=donor_id,  
                organization_id=organization.id,
                is_anonymous=is_anonymous,
            )

            # Save the donation in the database
            db.session.add(donation)
            db.session.commit()

            return {
                "donation": donation,
                "client_secret": CreatePaymentIntentResource(amount),
            }, 201

        except Exception as e:
            return {"error": str(e)}, 400


@donation_ns.route("/<int:id>")
class DonationDetailResource(Resource):
    @donation_ns.marshal_with(donation_response)
    @jwt_required()
    def get(self, id):
        """Get details of a donation by ID."""
        donation = Donation.query.get(id)
        if donation is None:
            api.abort(404, "Donation not found")
        return donation
