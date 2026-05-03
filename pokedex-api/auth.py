# ---------------------
# IMPORTS
# ---------------------
from flask import Blueprint, request, jsonify
from functools import wraps        # needed to preserve function names in decorators
from dotenv import load_dotenv     # loads .env file
from werkzeug.security import check_password_hash  # safely compare hashed passwords
import os
import jwt                         # PyJWT library for creating/validating tokens
from datetime import datetime, timedelta  # for setting token expiry time
from database import users         # our user list

load_dotenv()

# ---------------------
# CONFIG
# ---------------------
SECRET_KEY = os.getenv("SECRET_KEY")          # key used to sign JWT tokens
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION"))  # how many minutes token is valid
tokens = {}  # dictionary that stores all valid tokens {token: user}

auth_bp = Blueprint("auth", __name__)  # blueprint for auth routes

# ---------------------
# LOGIN
# ---------------------
@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()          # get JSON body from request
    username = data.get("username")
    password = data.get("password")

    # find user in database by username
    user = next((u for u in users if u["username"] == username), None)

    # check if user exists AND password matches the hashed password
    if user and check_password_hash(user["password"], password):

        # payload = data we store INSIDE the token
        payload = {
            "username": user["username"],
            "id": user["id"],
            "exp": datetime.now().astimezone() + timedelta(minutes=JWT_EXPIRATION)  # expiry time
        }

        # create the JWT token using our secret key
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        # store token in our tokens dict so we can look up the user later
        tokens[token] = user

        return jsonify({"token": token})  # send token back to client

    return jsonify({"error": "Invalid credentials"}), 401  # wrong username or password

# ---------------------
# LOGOUT
# ---------------------
@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    auth_header = request.headers.get("Authorization")  # get Authorization header
    if not auth_header:
        return jsonify({"error": "Missing token"}), 401

    token = auth_header.split(" ")[1]  # extract token from "Bearer <token>"
    tokens.pop(token, None)            # delete token from valid tokens dict
    return jsonify({"message": "Logged out successfully"})

# ---------------------
# REQUIRE AUTH decorator
# checks if the JWT token is valid before allowing access
# usage: add @require_auth above any protected route
# ---------------------
def require_auth(f):
    @wraps(f)  # preserves the original function name
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        # check if Authorization header exists and starts with "Bearer "
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401

        token = auth_header.split(" ")[1]  # extract token from header

        try:
            # decode and verify the token using our secret key
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = payload  # attach decoded user info to the request

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401  # token is too old

        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401  # token is fake/tampered

        return f(*args, **kwargs)  # token is valid, continue to the route
    return decorated

# ---------------------
# REQUIRE ROLE decorator
# checks if the logged in user has the required role
# usage: add @require_role(["admin", "editor"]) above a protected route
# ---------------------
def require_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            # check if Authorization header exists
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Authentication required"}), 401

            token = auth_header.split(" ")[1]

            # check if token is in our valid tokens dict (not logged out)
            if token not in tokens:
                return jsonify({"error": "Invalid or expired token"}), 401

            user = tokens[token]  # get the full user object

            # check if user's role is in the list of allowed roles
            if user["role"] not in allowed_roles:
                return jsonify({"error": "Forbidden"}), 403  # wrong role

            request.user = user  # attach user to request
            return f(*args, **kwargs)  # role is allowed, continue to route
        return decorated
    return decorator