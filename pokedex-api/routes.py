from flask import Blueprint, request, jsonify
from database import pokemon          # ← import pokemon list from database.py
from auth import require_auth, require_role  # ← import our decorators from auth.py

# create a blueprint for pokemon routes
# instead of @app.route we now use @pokemon_bp.route
pokemon_bp = Blueprint("pokemon", __name__)

# ---------------------
# HEALTH CHECK
# no auth needed, anyone can check if API is running
# ---------------------
@pokemon_bp.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# ---------------------
# GET all pokemon
# @require_auth added here because only logged in users can see pokemon
# no @require_role because ALL roles (admin, editor, viewer) can see this
# ---------------------
@pokemon_bp.route("/api/pokemon", methods=["GET"])
@require_auth                          # ← must be logged in
def get_all_pokemon():
    return jsonify(pokemon)

# ---------------------
# GET single pokemon by id
# @require_auth added here because only logged in users can see pokemon
# <int:pokemon_id> means Flask expects a number in the URL
# ---------------------
@pokemon_bp.route("/api/pokemon/<int:pokemon_id>", methods=["GET"])
@require_auth                          # ← must be logged in
def get_pokemon(pokemon_id):
    found = find_pokemon(pokemon_id)
    if not found:
        return jsonify({"error": "Pokemon not found"}), 404
    return jsonify(found)

# ---------------------
# SEARCH pokemon by name
# @require_auth added here because only logged in users can search
# uses query parameter: /api/pokemon/search?name=pikachu
# ---------------------
@pokemon_bp.route("/api/pokemon/search", methods=["GET"])
@require_auth                          # ← must be logged in
def search_pokemon():
    name = request.args.get("name")    # ← gets the ?name= part from the URL
    if not name:
        return jsonify({"error": "No name provided"}), 400
    found = next((p for p in pokemon if p["name"].lower() == name.lower()), None)
    if not found:
        return jsonify({"error": "Pokemon not found"}), 404
    return jsonify(found)

# ---------------------
# POST new pokemon
# @require_auth added because user must be logged in
# @require_role(["admin", "editor"]) added because viewers cannot add pokemon
# both decorators needed: first check login, then check role
# ---------------------
@pokemon_bp.route("/api/pokemon", methods=["POST"])
@require_auth                          # ← step 1: must be logged in
@require_role(["admin", "editor"])     # ← step 2: must be admin or editor
def create_pokemon():
    data = request.get_json()          # ← get the JSON body sent by client
    new_pokemon = {
        "id": generate_id(),           # ← auto generate next id
        "name": data.get("name"),
        "type": data.get("type"),
        "hp": data.get("hp")
    }
    pokemon.append(new_pokemon)        # ← add to our in-memory list
    return jsonify(new_pokemon), 201   # ← 201 means "created successfully"

# ---------------------
# PUT update pokemon
# @require_auth added because user must be logged in
# @require_role(["admin", "editor"]) added because viewers cannot edit pokemon
# ---------------------
@pokemon_bp.route("/api/pokemon/<int:pokemon_id>", methods=["PUT"])
@require_auth                          # ← step 1: must be logged in
@require_role(["admin", "editor"])     # ← step 2: must be admin or editor
def update_pokemon(pokemon_id):
    found = find_pokemon(pokemon_id)
    if not found:
        return jsonify({"error": "Pokemon not found"}), 404
    data = request.get_json()
    found.update(data)                 # ← update only the fields that were sent
    return jsonify(found)

# ---------------------
# DELETE pokemon
# @require_auth added because user must be logged in
# @require_role(["admin"]) added because ONLY admin can delete
# editors and viewers will get 403 Forbidden
# ---------------------
@pokemon_bp.route("/api/pokemon/<int:pokemon_id>", methods=["DELETE"])
@require_auth                          # ← step 1: must be logged in
@require_role(["admin"])               # ← step 2: must be admin ONLY
def delete_pokemon(pokemon_id):
    found = find_pokemon(pokemon_id)
    if not found:
        return jsonify({"error": "Pokemon not found"}), 404
    pokemon.remove(found)
    return "", 204                     # ← 204 means "deleted, no content to return"

# ---------------------
# HELPER FUNCTIONS
# these are not routes, just utility functions used above
# ---------------------

# finds a pokemon by its id, returns None if not found
def find_pokemon(pokemon_id):
    return next((p for p in pokemon if p["id"] == pokemon_id), None)

# generates next available id by taking the highest current id and adding 1
def generate_id():
    return max(p["id"] for p in pokemon) + 1 if pokemon else 1