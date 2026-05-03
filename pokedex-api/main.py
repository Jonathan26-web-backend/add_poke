from flask import Flask
from flask_cors import CORS
from routes import pokemon_bp    # ← import pokemon blueprint
from auth import auth_bp         # ← import auth blueprint

app = Flask(__name__)
CORS(app)                        # ← allows frontend to talk to backend

# register blueprints
# this activates all the routes defined in routes.py and auth.py
app.register_blueprint(auth_bp)      # ← activates /api/login and /api/logout
app.register_blueprint(pokemon_bp)   # ← activates all /api/pokemon routes

if __name__ == "__main__":
    app.run(debug=True)