"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_user():
    users = User.query.all()
    result = [user.serialize() for user in users]
    return jsonify(result), 200

# [GET] Listar todos los registros de people
@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    result = [person.serialize() for person in people]
    return jsonify(result), 200

# [GET] Mostrar la información de un solo personaje según su id
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Character.query.get(people_id)
    if person:
        return jsonify(person.serialize()), 200
    else:
        return jsonify({'error': 'Person not found'}), 404

@app.route('/planets', methods=['GET'])
def get_planets():
# select * from planet
   planets = Planet.query.all()
   result = [planet.serialize()for planet in planets]
   return jsonify(result), 200

# [GET] Mostrar la información de un solo planeta según su id
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    else:
        return jsonify({'error': 'Planet not found'}), 404
    
@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def favorite_character(character_id):
    favorite = Favorite(user_id = 1, character_id = character_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def favorite_planet(planet_id):
    favorite = Favorite(user_id = 1, planet_id = planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 200

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    favorite = Favorite.query.filter(db.and_(Favorite.user_id == 1, Favorite.character_id == character_id)).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 200
    else:
        return jsonify({'error': 'Character not found'}), 404

#select * from favorite where user_id = 1 and planet_id = 1
#Character.query.get(people_id)
#db.and_(Favorite.user_id == 1, Favorite.character_id == 2)

@app.route('/favorite/planet/<int:character_id>', methods=['DELETE'])
def delete_planet(planet_id):
    favorite = Favorite.query.filter(db.and_(Favorite.user_id == 1, Favorite.planet_id == planet_id)).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify(favorite.serialize()), 200
    else:
        return jsonify({'error': 'Planet not found'}), 404
    
    
#favorite = Favorite(user_id=1, character_id=2)
#db.session.add(favorite)
#db.session.commit()
    

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
