from flask import Flask, request, redirect, url_for
from flask_restful import Api, Resource
import re
from models import db, Feedback

app = Flask(__name__)

# SQLite config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///feedback.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
api = Api(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return redirect(url_for("feedback"))

# ------------------ Email Validator ------------------
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# ------------------ Resources ------------------
class FeedbackResource(Resource):
    def get(self):
        feedbacks = Feedback.query.all()
        return {
            "status": "success",
            "feedbacks": [f.to_dict() for f in feedbacks]
        }, 200

    def post(self):
        data = request.get_json()

        if not data:
            return {"status": "error", "message": "Missing JSON body"}, 400

        name = data.get("name")
        email = data.get("email")
        message = data.get("message")

        if not name or not email or not message:
            return {"status": "error", "message": "Name, Email, and Message are required"}, 400

        if not is_valid_email(email):
            return {"status": "error", "message": "Invalid email format"}, 400

        new_feedback = Feedback(name=name, email=email, message=message)
        db.session.add(new_feedback)
        db.session.commit()

        return {
            "status": "success",
            "message": f"Thank you {name}, your feedback has been received!",
            "feedback": new_feedback.to_dict()
        }, 201

# Register endpoint
api.add_resource(FeedbackResource, "/feedback", endpoint="feedback")

if __name__ == "__main__":
    app.run(debug=True)
