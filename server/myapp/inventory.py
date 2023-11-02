from flask import request, jsonify, make_response 
from flask_jwt_extended import jwt_required, get_jwt_identity
from myapp import db, jwt
from myapp.schema import inventory_schema , inventories_schema
from flask_restx import Namespace, Resource, fields
from myapp.models import  Inventory # Import your Story model
from . import api


inventory_model = api.model(
    "Inventory",
    {
        "id": fields.Integer(readonly=True),
        "name": fields.String,
        "quantity": fields.Integer,
        "beneficiary_id": fields.Integer,
    },
)

@api.route("/inventory")
class InventoryResource(Resource):
    @api.expect(inventory_model, validate=True)
    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            if current_user_id is None:
                return {"message": "Invalid token"}, 401

            inventory_items = Inventory.query.filter_by(beneficiary_id=current_user_id).all()
            inventory_list = inventories_schema.dump(inventory_items)
            res = inventory_list, 200
            return jsonify(res)
        except Exception as e:
            error_message = "An error occurred"
            return make_response(jsonify({"message": error_message}), 500)        
        
    @api.expect(inventory_model, validate=True)
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        try:
            new_inventory_item = api.payload  # Get the data for the new inventory item from the request
            inventory_item = Inventory(**new_inventory_item)
            db.session.add(inventory_item)
            db.session.commit()
            return jsonify({"message": "Inventory item created successfully"}), 201
        except Exception as e:
            error_message = "An error occurred while creating the inventory item"
            return make_response(jsonify({"message": error_message}), 500)

        

@api.route("/inventory/<int:inventory_id>")
class InventoryItemResource(Resource):
    @jwt_required()
    def get(self, inventory_id):
        current_user_id = get_jwt_identity()
        try:
            inventory_item = Inventory.query.get(inventory_id)
            if inventory_item:
                inventory_data = inventory_schema.dump(inventory_item)
                return inventory_data, 200
            else:
                return {"message": "Inventory item not found"}, 404
        except Exception as e:
            print("Error:", e)
            return {"message": "An error occurred"}, 500
    
    @jwt_required
    def delete(self, inventory_id):
        current_user_id = get_jwt_identity()
        try:
            inventory_item = Inventory.query.get(inventory_id)
            if inventory_item:
                db.session.delete(inventory_item)
                db.session.commit()
                return make_response(jsonify({"message": "Inventory item deleted successfully"}), 204)
            else:
                return make_response(jsonify({"message": "Inventory item not found"}), 404)
        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return make_response(jsonify({"message": "An error occurred while deleting the inventory item"}), 500)
    
    @jwt_required()
    def patch(self, inventory_id): 
        current_user_id = get_jwt_identity()
        try:
            inventory_item = Inventory.query.get(inventory_id)
            if not inventory_item:
               return make_response(jsonify({"message": "Inventory item not found"}), 404)


            updated_data = api.payload  # Get the data for updating the inventory item from the request

            # Update the inventory item's fields with the new data
            for key, value in updated_data.items():
                setattr(inventory_item, key, value)

            db.session.commit()
            return make_response(jsonify({"message": "Inventory item updated successfully"}), 200)
        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return make_response(jsonify({"message": "An error occurred while updating the inventory item"}), 500)