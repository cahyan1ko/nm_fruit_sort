from flask import Blueprint, jsonify
from ..db import get_db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Hello, Flask!"

@main.route('/fruits')
def get_fruits():
    db = get_db()
    fruits = list(db.users.find({}, {"_id": 0}))
    return jsonify(fruits)
