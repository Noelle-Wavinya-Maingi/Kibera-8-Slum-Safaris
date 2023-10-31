from flask import request, jsonify, make_response
from flask_restx import Namespace, Resource, fields
from myapp.models import Story  # Import your Story model
from . import api

# stories_ns = Namespace("stories", description="Stories related operations")

story_model = api.model(
    "Story",
    {
        "id": fields.Integer(readonly=True),
        "title": fields.String,
        "content": fields.String,
        "created_at": fields.DateTime(dt_format="iso8601"),
        "organization_id": fields.Integer,
        "image": fields.String,
    },
)

@api.route("/stories")
class StoriesResource(Resource):
    @api.expect(story_model, validate=True)
    def get(self):
        try:
            stories = Story.query.all()
            stories_list = [stori.to_dict() for stori in stories]
            print(stories)
            res = make_response(jsonify(stories_list), 200)
            return res
        except Exception as e:
            print("Error:", e)
            return {"message": "An error occurred"}, 500
