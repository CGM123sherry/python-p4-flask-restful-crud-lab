#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

# Route for listing all plants and creating a new plant
class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)

api.add_resource(Plants, '/plants')

# Combined PlantByID class handling GET, PATCH, and DELETE
class PlantByID(Resource):

    def get(self, id):
        # Find plant by id
        plant = Plant.query.filter_by(id=id).first()

        if not plant:
            return make_response(jsonify({"error": "Plant not found"}), 404)

        # Return the plant as a JSON response
        return make_response(jsonify(plant.to_dict()), 200)

    def patch(self, id):
        # Find plant by id
        plant = Plant.query.filter_by(id=id).first()

        if not plant:
            return make_response(jsonify({"error": "Plant not found"}), 404)

        # Get the updated data from the request
        data = request.get_json()

        # Update the is_in_stock field if provided
        if 'is_in_stock' in data:
            plant.is_in_stock = data['is_in_stock']

        # Commit the changes to the database
        db.session.commit()

        # Return the updated plant data
        return make_response(jsonify(plant.to_dict()), 200)

    def delete(self, id):
        # Find plant by id
        plant = Plant.query.filter_by(id=id).first()

        if not plant:
            return make_response(jsonify({"error": "Plant not found"}), 404)

        # Delete plant from the database
        db.session.delete(plant)
        db.session.commit()

        # Return a 204 No Content response
        return make_response('', 204)

# Register the PlantByID route with Flask-RESTful
api.add_resource(PlantByID, '/plants/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
