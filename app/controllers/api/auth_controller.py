from flask import Blueprint, request
from ...db import get_db
from werkzeug.security import check_password_hash, generate_password_hash
from ...utils.response import success, error

from flask import current_app as app
from dotenv import load_dotenv

import datetime
import os
import jwt
import re

load_dotenv()

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", 24))

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not all(k in data for k in ("name", "email", "password")):
        return error("Data tidak lengkap", 400)

    name = data['name']
    email = data['email']

    if not EMAIL_REGEX.match(email):
        return error("Email tidak valid", 400)

    password = generate_password_hash(data['password'])
    role = "user"

    db = get_db()

    if db.users.find_one({"email": email}):
        return error("Email sudah terdaftar", 409)

    db.users.insert_one({
        "name": name,
        "email": email,
        "password": password,
        "role": role
    })

    return success({"name": name, "email": email}, "Register berhasil", 201)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not all(k in data for k in ("email", "password")):
        return error("Data tidak lengkap", 400)

    email = data['email']

    if not EMAIL_REGEX.match(email):
        return error("Email tidak valid", 400)
    
    password = data['password']
    db = get_db()

    user = db.users.find_one({"email": email})
    if not user:
        return error("Email tidak ditemukan", 404)

    if not check_password_hash(user['password'], password):
        return error("Password salah", 401)
    
    payload = {
        "email": user["email"],
        "name": user["name"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRE_HOURS)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return success({"token": token}, "Login berhasil", 200)