from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from myapp import db, jwt, api, inventory_ns
from myapp.schema import inventory_schema, inventories_schema
from flask_restx import  Resource, fields
from myapp.models import Inventory


inventory_model = inventory_ns.model(
    "Inventory",
    {
        "id": fields.Integer(readonly=True),
        "name": fields.String,
        "quantity": fields.Integer,
        "user_id": fields.Integer,
    },
)

@inventory_ns.route("")
class InventoryResource(Resource):
    @inventory_ns.expect(inventory_model, validate=True)
    @jwt_required()
    def get(self):
        """Get the list of invetories"""
        try:
            current_user_id = get_jwt_identity()
            if current_user_id is None:
                return {"message": "Invalid token"}, 401

            inventory_items = Inventory.query.filter_by(user_id=current_user_id).all()
            inventory_list = inventories_schema.dump(inventory_items)
            res = inventory_list, 200
            return jsonify(res)
        except Exception as e:
            error_message = "An error occurred"
            return make_response(jsonify({"message": error_message}), 500)

    @inventory_ns.expect(inventory_model, validate=True)
    @jwt_required()
    def post(self):
        """Post an inventory"""
        current_user_id = get_jwt_identity()
        try:
            new_inventory_item = (
                api.payload
            )  # Get the data for the new inventory item from the request
            new_inventory_item["user_id"] = current_user_id
            inventory_item = Inventory(**new_inventory_item)
            db.session.add(inventory_item)
            db.session.commit()
            return {"message": "Inventory item created successfully"}, 201
        except Exception as e:
            error_message = "An error occurred while creating the inventory item"
            return {"message": error_message}, 500

@inventory_ns.route("<int:inventory_id>")
class InventoryItemResource(Resource):
    @jwt_required()
    def get(self, inventory_id):
        """Get an invetory by ID"""
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

    @jwt_required()
    def delete(self, inventory_id):
        """Delete an inventory"""
        try:
            current_user_id = get_jwt_identity()
            inventory_item = Inventory.query.get(inventory_id)
            if inventory_item:
                db.session.delete(inventory_item)
                db.session.commit()
                return {"message": "Inventory item deleted successfully"}, 204
            else:
                return {"message": "Inventory item not found"}, 404
        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return {
                "message": "An error occurred while deleting the inventory item"
            }, 500

    @jwt_required()
    def patch(self, inventory_id):
        """Update an inventory"""
        current_user_id = get_jwt_identity()
        try:
            inventory_item = Inventory.query.get(inventory_id)
            if not inventory_item:
                return {"message": "Inventory item not found"}, 404

            updated_data = (
                api.payload
            )  # Get the data for updating the inventory item from the request

            # Update the inventory item's fields with the new data
            for key, value in updated_data.items():
                setattr(inventory_item, key, value)

            db.session.commit()
            return {"message": "Inventory item updated successfully"}, 200
        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return {
                "message": "An error occurred while updating the inventory item"
            }, 500
