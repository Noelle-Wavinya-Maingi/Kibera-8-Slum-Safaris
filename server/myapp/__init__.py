import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import logging
from dotenv import load_dotenv

load_dotenv()



from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask import Flask
from flask_restx import Api, Namespace
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_marshmallow import Marshmallow
import stripe
from flask_cors import CORS


app = Flask(__name__)
api = Api(app, version="1.0", title="Kibera 8 Slum Safaris API")
ma = Marshmallow(app)
app.config["SECRET_KEY"] = "33f334a749dd2e8216f245b0bb263aea"
app.config["JWT_SECRET_KEY"] = "b99ce1e67619ed6f9dd29211ec08e559"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "noemaingi@gmail.com"
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEBUG"] = os.getenv("MAIL_DEBUG", True)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.json.compact = False

stripe_keys = {
    "secret_key": os.getenv("STRIPE_SECRET_KEY"),
    "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY"),
}

stripe.api_key = stripe_keys["secret_key"]
# Configure Cloudinary
cloudinary.config(
    cloud_name='ddi2x0uf9',
    api_key='677945454898332',
    api_secret='GmNEkzXoXwSrY-1MkfSBZ255FD4'
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)
jwt = JWTManager(app)
cors = CORS(app)

# Create namespaces for different resource types
beneficiary_ns = Namespace("Beneficiaries", description="Beneficiary related operations")
booking_ns = Namespace("Bookings", description="Tour booking related operations")
donation_ns = Namespace("Donations", description="Donation related operations")
inventory_ns = Namespace("Inventory", description="Inventory related operations")
organization_ns = Namespace("Organization", description="Organization related operations")
story_ns = Namespace("Story", description="Story related operations")
tour_ns = Namespace("Tour", description="Tour related operations")
user_ns = Namespace("User", description="User related operations")

# Add namespaces to the API instance
api.add_namespace(beneficiary_ns)
api.add_namespace(donation_ns)
api.add_namespace(booking_ns)
api.add_namespace(user_ns)
api.add_namespace(inventory_ns)
api.add_namespace(organization_ns)
api.add_namespace(story_ns)
api.add_namespace(tour_ns)

