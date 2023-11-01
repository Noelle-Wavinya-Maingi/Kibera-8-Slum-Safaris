from flask import request, jsonify, make_response 
from myapp import db
from myapp.schema import story_schema, stories_schema
from flask_restx import Namespace, Resource, fields
from myapp.models import Story , Tours  # Import your Story model
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
            stories_list = stories_schema.dump(stories)
            print(stories)
            res = stories_list, 200
            return res
        except Exception as e:
            print("Error:", e)
            return {"message": "An error occurred"}, 500
    
    @api.expect(story_model, validate=True)
    def post(self):
        try:
            new_story = api.payload  # Get the data for the new story from the request
            story = Story(**new_story)
            db.session.add(story)
            db.session.commit()
            return {"message": "Story created successfully"}, 201
        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return {"message": "An error occurred while creating the story"}, 500
        

@api.route("/stories/<int:story_id>")
class StoryResource(Resource):
        def get(self, story_id):
            try:
                story = Story.query.get(story_id)
                if story:
                    story_data = story_schema.dump(story)
                    return story_data, 200
                else:
                    return {"message": "Story not found"}, 404
            except Exception as e:
                print("Error:", e)
                return {"message": "An error occurred"}, 500
            
        def delete(self, story_id):
            try:
                story = Story.query.get(story_id)
                if story:
                    db.session.delete(story)
                    db.session.commit()
                    return {"message": "Story deleted successfully"}, 204
                else:
                    return {"message": "Story not found"}, 404
            except Exception as e:
                print("Error:", e)
                db.session.rollback()
                return {"message": "An error occurred while deleting the story"}, 500


