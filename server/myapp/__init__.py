from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask import Flask
import os
from flask_restx import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta

app = Flask(__name__)
api = Api(app, version="1.0", title="Kibera 8 Slum Safaris API")
app.config["SECRET_KEY"] = '33f334a749dd2e8216f245b0bb263aea'
app.config['JWT_SECRET_KEY'] = 'b99ce1e67619ed6f9dd29211ec08e559'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tours.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'noemaingi@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  
app.config['MAIL_DEBUG'] = os.getenv('MAIL_DEBUG', True)  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days = 30)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(minutes = 15)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)
jwt = JWTManager(app)
