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
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register User
    ---
    tags:
      - Auth
    description: Endpoint untuk registrasi user baru dengan validasi email dan password yang kuat.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: Hanzo
            email:
              type: string
              example: hanzo@example.com
            password:
              type: string
              example: Halo12!!
    responses:
      201:
        description: Registrasi berhasil
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: true
            message:
              type: string
              example: Register berhasil
            data:
              type: object
              properties:
                name:
                  type: string
                  example: Hanzo
                email:
                  type: string
                  example: hanzo@example.com
      400:
        description: Data tidak lengkap atau format tidak valid
      409:
        description: Email sudah terdaftar
    """
    ...
    data = request.get_json()

    if not data or not all(k in data for k in ("name", "email", "password")):
        return error("Data tidak lengkap", 400)

    name = data['name']
    email = data['email']
    password_plain = data['password']

    if not EMAIL_REGEX.match(email):
        return error("Email tidak valid", 400)

    if not PASSWORD_REGEX.match(password_plain):
        return error(
            "Password harus minimal 8 karakter, mengandung huruf besar, huruf kecil, angka, dan simbol", 400
        )
    
    password_hashed = generate_password_hash(password_plain)
    role = "user"
    db = get_db()
    if db.users.find_one({"email": email}):
        return error("Email sudah terdaftar", 409)
    db.users.insert_one({
        "name": name,
        "email": email,
        "password": password_hashed,
        "role": role
    })

    return success({"name": name, "email": email}, "Register berhasil", 201)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login User
    ---
    tags:
      - Auth
    description: Endpoint untuk login user menggunakan email dan password. Akan mengembalikan JWT token jika berhasil.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: hanzo@example.com
            password:
              type: string
              example: Halo12!!
    responses:
      200:
        description: Login berhasil
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: true
            message:
              type: string
              example: Login berhasil
            data:
              type: object
              properties:
                token:
                  type: string
                  example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
      400:
        description: Data tidak lengkap atau email tidak valid
      401:
        description: Password salah
      404:
        description: Email tidak ditemukan
    """
    ...
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