from dotenv import load_dotenv
load_dotenv()  
from myapp import app, db, routes , tours_routes , inventory, admin_routes , bookings
from myapp.models import User, Organization

if __name__ == "__main__":
    app.run(debug=True)
