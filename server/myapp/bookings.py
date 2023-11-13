from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from flask_restx import Resource, fields
from flask_mail import Message

# Import necessary models and libraries
from myapp.models import user_tours, Tours, User
from myapp import api, db, mail, booking_ns, stripe

# Define Data Transfer Object for booking information
booking_info = booking_ns.model(
    "BookingInfo",
    {
        "tour_name": fields.String(required=True, description="ID of the tour to book"),
        "tour_date": fields.Date(
            required=True, description="Date of the tour in YYYY-MM-DD format"
        ),
        "number_of_persons": fields.Integer(
            required=True, description="Number of persons on the tour"
        ),
    },
)


# Function to calculate the total booking amount
def calculate_booking_amount(tour, number_of_persons):
    base_price = tour.price

    total_price = base_price * number_of_persons

    return total_price


# Function to send an email confirmation to the user
def send_booking_confirmation_email(
    user_email, user_username, tour_name, tour_date, booking_amount 
):
    msg = Message(
        "Tour Booking Confirmation", sender="noreply@gmail.com", recipients=[user_email]
    )

    msg.body = (
        f"Hello {user_username},\n"
        + f"Thank you for booking the {tour_name} tour for {tour_date}. The total amount is USD{booking_amount}. Enjoy your trip!\n\n"
        + "Regards,\n"
        + "Kibera-8 Slum Safaris"
    )
    mail.send(msg)

def send_booking_approval_email(
    user_email, user_username, tour_name, tour_date, booking_amount
):
    msg = Message(
        "Tour Booking Approved", sender="noreply@gmail.com", recipients=[user_email]
    )

    msg.body = (
        f"Hello {user_username},\n"
        + f"Your booking for the {tour_name} tour on {tour_date} has been approved. The total amount is USD{booking_amount}. Enjoy your trip!\n\n"
        + "Regards,\n"
        + "Kibera-8 Slum Safaris"
    )
    mail.send(msg)


@booking_ns.route("/")
class BookTour(Resource):
    @api.expect(booking_info, validate=True)
    @jwt_required()
    def post(self):
        """Post a booking for a tour"""
        current_user_id = get_jwt_identity()
        data = request.get_json()

        user_id = current_user_id
        tour_name = data.get("tour_name")
        tour_date = data.get("tour_date")
        number_of_persons = data.get("number_of_persons")

        # Input validation
        if not tour_name:
            return {"message": "Tour name is required"}, 400

        if not tour_date:
            return {"message": "Tour date is required"}, 400

        if number_of_persons < 1:
            return {"message": "Number of persons must be at least 1"}, 400

        # Lookup the tour name based on the provided tour_id
        tour = Tours.query.filter_by(name=tour_name).first()

        if not tour:
            return {"message": "Tour not found"}, 404

        try:
            # Calculate the booking amount
            booking_amount = calculate_booking_amount(tour, number_of_persons)

            # Insert booking information into the database
            user_tour_entry = user_tours.insert().values(
                user_id=user_id, tours_id=tour.id, tour_date=tour_date
            )
            db.session.execute(user_tour_entry)
            db.session.commit()

            # Create a Payment Intent using the Stripe API
            payment_intent = stripe.PaymentIntent.create(
                amount=int(booking_amount * 100), currency="usd"
            )

            # Get the user's email from the users table
            user = User.query.get(user_id)
            user_email = user.email
            user_username = user.username

            # Send an email to the user
            send_booking_confirmation_email(
                user_email, user_username, tour.name, tour_date, booking_amount
            )

            # Return the tour information and date as a JSON response
            response_data = {
                "message": "Tour booked successfully!",
                "tour_id": tour.id,
                "tour_name": tour.name,
                "tour_date": tour_date,
                "tour_price": tour.price,
                "number_of_persons": number_of_persons,
                "total_price": booking_amount,
                "client_secret": payment_intent.client_secret,
            }
            return response_data, 201
        except Exception as e:
            return {"message": "Error while booking the tour", "error": str(e)}, 500

@booking_ns.route("/admin-approval/<int:booking_id>")
class AdminApprovalResource(Resource):
    @jwt_required()
    def put(self, booking_id):
        current_user_id = get_jwt_identity()

        # Check if the current user is the admin (you may need additional logic for role-based authentication)
        admin_user = User.query.filter_by(id=current_user_id, is_admin=True).first()
        if not admin_user:
            return {"message": "Unauthorized"}, 401

        # Update the booking status to approved
        booking = user_tours.query.get(booking_id)
        if not booking:
            return {"message": "Booking not found"}, 404

        booking.is_approved = True
        db.session.commit()

        # Send an email to the user informing them of the approval (similar to the booking confirmation email)
        send_booking_approval_email(
            booking.user.email,
            booking.user.username,
            booking.tour.name,
            booking.tour_date,
            booking.total_price,
        )

        return {"message": f"Booking {booking_id} approved successfully"}, 200
