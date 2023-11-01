from flask import request, jsonify, make_response 
from myapp import db
from myapp.schema import story_schema, stories_schema ,tour_schema , tours_schema
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

tour_model = api.model(
    "Tour",
    {
        "id": fields.Integer(readonly=True),
        "name": fields.String,
        "image": fields.String,
        "price": fields.Float,
    },
)


@api.route("/tours")
class ToursResource(Resource):
    @api.expect(tour_model, validate=True)
    def get(self):
        try:
            tours = Tours.query.all()
            tours_list = tours_schema.dump(tours)
            print(tours)
            res = tours_list, 200
            return res
        except Exception as e:
            print("Error:", e)
            return {"message": "An error occurred"}, 500
    
    @api.expect(tour_model, validate=True)
    def post(self):
        try:
            new_tour = api.payload
            tour = Tours(**new_tour)
            db.session.add(tour)
            db.session.commit()
            return {"message": "Tour created successfully"}, 201
        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return {"message": "An error occurred while creating the tour"}, 500


@api.route("/tours/<int:tour_id>")
class TourResource(Resource):
    def get(self, tour_id):
        try:
            tour = Tours.query.get(tour_id)
            if tour:
                tour_data = tour_schema.dump(tour)  # Use tour_schema instead of tours_schema
                return tour_data, 200
            else:
                return {"message": "Tour not found"}, 404
        except Exception as e:
            print("Error:", e)
            return {"message": "An error occurred"}, 500
        
    def delete(self, tour_id):
        try:
            tour = Tours.query.get(tour_id)
            if tour:
                db.session.delete(tour)
                db.session.commit()
                return {"message": "Tour deleted successfully"}, 204
            else:
                return {"message": "Tour not found"}, 404
        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return {"message": "An error occurred while deleting the tour"}, 500
        
@api.route("/tours/<int:tour_id>")
class TourResource(Resource):
    @api.expect(tour_model, validate=True)
    def patch(self, tour_id):
        try:
            tour = Tours.query.get(tour_id)
            if not tour:
                return {"message": "Tour not found"}, 404

            data = api.payload

            for key, value in data.items():
                setattr(tour, key, value)

            db.session.commit()

            return {"message": "Tour updated successfully"}, 200
        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return {"message": "An error occurred while updating the tour"}, 500






