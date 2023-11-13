from myapp import db
from flask_jwt_extended import jwt_required
from myapp.schema import story_schema, stories_schema, tour_schema, tours_schema
from flask_restx import Resource, fields
from myapp.models import Story, Tours, Organization
from . import api, story_ns, tour_ns
import cloudinary.uploader

story_model = story_ns.model(
    "Story",
    {
        "id": fields.Integer(readonly=True),
        "title": fields.String,
        "content": fields.String,
        "created_at": fields.DateTime(dt_format="iso8601"),
        "organization_name": fields.String,
        "image": fields.String,
    },
)

tour_model = tour_ns.model(
    "Tour",
    {
        "id": fields.Integer(readonly=True),
        "name": fields.String,
        "image": fields.String,
        "price": fields.Float,
    },
)


@story_ns.route("/")
class StoriesResource(Resource):
    @story_ns.expect(story_model, validate=True)
    def get(self):
        """Get a list of stories"""
        try:
            stories = Story.query.all()
            stories_list = stories_schema.dump(stories)
            print(stories)
            res = stories_list, 200
            return res
        except Exception as e:
            print("Error:", e)
            return {"message": "An error occurred"}, 500

    @story_ns.expect(story_model, validate=True)
    @jwt_required()
    def post(self):
        """Post a new story"""
        try:
            new_story = api.payload

            organization_name = new_story.get("organization_name")

            organization = Organization.query.filter_by(name=organization_name).first()

            if not organization:
                return {"message": "Organization not found"}, 404

            new_story["organization_id"] = organization.id
            new_story.pop("organization_name")

            # Upload image to Cloudinary
            image_url = cloudinary.uploader.upload(new_story["image"])["url"]
            new_story["image"] = image_url

            story = Story(**new_story)
            db.session.add(story)
            db.session.commit()
            return {"message": "Story created successfully"}, 201

        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return {"message": "An error occurred while creating the story"}, 500


@story_ns.route("/<int:story_id>")
class StoryResource(Resource):
    def get(self, story_id):
        """Get a story by ID"""
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

    @jwt_required()
    def delete(self, story_id):
        """Delete a story"""
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


@tour_ns.route("/")
class ToursResource(Resource):
    @tour_ns.expect(tour_model, validate=True)
    def get(self):
        """Get a list of tours"""
        try:
            tours = Tours.query.all()
            tours_list = tours_schema.dump(tours)
            print(tours)
            res = tours_list, 200
            return res
        except Exception as e:
            print("Error:", e)
            return {"message": "An error occurred"}, 500

    @tour_ns.expect(tour_model, validate=True)
    @jwt_required()
    def post(self):
        """Post a new tour"""
        try:
            new_tour = api.payload

            # Upload image to Cloudinary
            image_url = cloudinary.uploader.upload(new_tour["image"])["url"]
            new_tour["image"] = image_url

            tour = Tours(**new_tour)
            db.session.add(tour)
            db.session.commit()
            return {"message": "Tour created successfully"}, 201

        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return {"message": "An error occurred while creating the tour"}, 500


@tour_ns.route("/<int:tour_id>")
class TourResource(Resource):
    def get(self, tour_id):
        """Get a tour by ID"""
        try:
            tour = Tours.query.get(tour_id)
            if tour:
                tour_data = tour_schema.dump(
                    tour
                )  
                return tour_data, 200
            else:
                return {"message": "Tour not found"}, 404
        except Exception as e:
            print("Error:", e)
            return {"message": "An error occurred"}, 500
        
    @jwt_required()
    def delete(self, tour_id):
        """Delete a tour"""
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
    
    @tour_ns.expect(tour_model, validate=True)
    @jwt_required()
    def patch(self, tour_id):
        """Update a tour"""
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
