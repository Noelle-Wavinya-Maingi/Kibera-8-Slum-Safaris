from myapp import app, db, routes
from myapp.models import User, Organization

if __name__ == "__main__":
    app.run(debug=True)
