
#  # Beneficiaries, donor and admin routes

# # Routes for Beneficiaries
# @app.route('/beneficiaries')
# def list_beneficiaries():
#     beneficiaries = Beneficiary.query.all()
#     return render_template('beneficiaries.html', beneficiaries=beneficiaries)

# @app.route('/beneficiary/<int:id>')
# def view_beneficiary(id):
#     beneficiary = Beneficiary.query.get(id)
#     return render_template('beneficiary.html', beneficiary=beneficiary)

# # Routes for Donors
# @app.route('/donors')
# def list_donors():
#     donors = User.query.filter_by(role='donor').all()
#     return render_template('donors.html', donors=donors)

# @app.route('/donor/<int:id>')
# def view_donor(id):
#     donor = User.query.get(id)
#     return render_template('donor.html', donor=donor)

# # Routes for Admin
# @app.route('/admin/dashboard')
# def admin_dashboard():
#     # Add admin authentication logic here
#     return render_template('admin/dashboard.html')

# @app.route('/admin/approve_organization/<int:id>')
# def approve_organization(id):
#     organization = Organization.query.get(id)
#     if organization.approve_request():
#         flash('Organization approved and notified.')
#     else:
#         flash('Organization is already approved.')
#     return redirect(url_for('admin_dashboard'))

# @app.route('/admin/reject_organization/<int:id>', methods=['GET', 'POST'])
# def reject_organization(id):
#     organization = Organization.query.get(id)
#     if request.method == 'POST':
#         reason = request.form['reason']
#         if organization.reject_request(reason):
#             flash('Organization rejected and notified.')
#             return redirect(url_for('admin_dashboard'))
#     return render_template('admin/reject_organization.html', organization=organization)


# if __name__ == '__main__':
#     app.run()

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
    def get(self):
        """Get a list of beneficiaries."""
        beneficiaries = Beneficiary.query.all()
        return beneficiaries

    @api.expect(beneficiary_request, validate=True)
    @api.marshal_with(beneficiary_request)
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
    def get(self, id):
        """Get details of a beneficiary by ID."""
        beneficiary = Beneficiary.query.get(id)
        if beneficiary is None:
            api.abort(404, "Beneficiary not found")
        return beneficiary

@api.route("/donations")
class DonationResource(Resource):
    @api.marshal_with(donation_request)
    def get(self):
        """Get a list of donations."""
        donations = Donation.query.all()
        return donations

    @api.expect(donation_request, validate=True)
    @api.marshal_with(donation_request)
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
    def get(self, id):
        """Get details of a donation by ID."""
        donation = Donation.query.get(id)
        if donation is None:
            api.abort(404, "Donation not found")
        return donation

@api.route("/admin/organization_requests/<int:id>")
class AdminOrganizationRequestResource(Resource):
    @api.marshal_with(organization_request)
    def get(self, id):
        """Get details of an organization request by ID."""
        organization = Organization.query.get(id)
        if organization is None:
            api.abort(404, "Organization request not found")
        return organization

    @api.expect(admin_action, validate=True)
    def put(self, id):
        """Approve or reject an organization request as an admin."""
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
