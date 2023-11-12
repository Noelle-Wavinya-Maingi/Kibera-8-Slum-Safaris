from dotenv import load_dotenv
load_dotenv()  
import cloudinary
import os

cloudinary.config(
    cloud_name=os.getenv('ddi2x0uf9'),
    api_key=os.getenv('677945454898332'),
    api_secret=os.getenv('GmNEkzXoXwSrY-1MkfSBZ255FD4')
)
from myapp import app, db, routes , tours_routes , inventory, admin_routes , bookings, forgotpass , superadmin
from myapp.models import User, Organization

if __name__ == "__main__":
    app.run(debug=True)
