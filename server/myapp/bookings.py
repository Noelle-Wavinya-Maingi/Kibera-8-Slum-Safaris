from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from flask_restx import Resource, fields

from myapp.models import user_tours, Tours
from myapp import api, db  # Replace this with your Flask app object

# Define Data Transfer Object for booking information
booking_info = api.model("BookingInfo", {
    "tour_name": fields.String(required=True, description="ID of the tour to book"),
    "tour_date": fields.Date(required=True, description="Date of the tour in YYYY-MM-DD format")
})

@api.route("/book_tour")
class BookTour(Resource):
    @api.expect(booking_info, validate=True)  
    @jwt_required()  
    def post(self):
        current_user_id = get_jwt_identity()
        data = request.get_json()

        user_id = current_user_id
        tour_name = data.get("tour_name")
        tour_date = data.get("tour_date")  

        if not tour_name:
            return {"message": "Tour name is required"}, 400

        if not tour_date:
            return {"message": "Tour date is required"}, 400

        # Lookup the tour name based on the provided tour_id
        tour = Tours.query.filter_by(name = tour_name).first()
        
        if not tour:
            return {"message": "Tour not found"}, 404

        try:
            user_tour_entry = user_tours.insert().values(
                user_id=user_id,
                tours_id=tour.id,
                tour_date=tour_date
            )
            db.session.execute(user_tour_entry)
            db.session.commit()

            # Return the tour information and date as a JSON response
            response_data = {
                "message": "Tour booked successfully!",
                "tour_name": tour.name,
                "tour_date": tour_date,
                "tour_price": tour.price
            }
            return response_data, 201
        except Exception as e:
            return {"message": "Error while booking the tour", "error": str(e)}, 500