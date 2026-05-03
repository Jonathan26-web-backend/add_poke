from dotenv import load_dotenv
load_dotenv()
import os
from werkzeug.security import generate_password_hash

users = [
    {
        "id": "6f8e1b9e-6a7c-4c7b-8a7c-5a7d0d9c2f2e",
        "username": os.getenv("ADMIN_USERNAME"),
        "password": generate_password_hash(os.getenv("ADMIN_PASSWORD")),
        "role": "admin"
    },
    {
        "id": "9c3f4d4e-3a52-4b1c-9c8c-7a2f1f9c1b8a",
        "username": os.getenv("EDITOR_USERNAME"),
        "password": generate_password_hash(os.getenv("EDITOR_PASSWORD")),
        "role": "editor"
    },
    {
        "id": "2e7a1c90-5d2b-4c0f-9e72-3b9a6c4d8f11",
        "username": os.getenv("VIEWER_USERNAME"),
        "password": generate_password_hash(os.getenv("VIEWER_PASSWORD")),
        "role": "viewer"
    }
]

#this can be done jsut uncomment it and commment bottom or you can import the file with all pokemone 
pokemon = [
    {"id": 1, "name": "Bulbasaur", "type": ["Grass", "Poison"], "hp": 45},
    {"id": 2, "name": "Charmander", "type": ["Fire"], "hp": 39},
    {"id": 3, "name": "Squirtle", "type": ["Water"], "hp": 44},
    {"id": 4, "name": "Pikachu", "type": ["Electric"], "hp": 35},
    {"id": 5, "name": "Mewtwo", "type": ["Psychic"], "hp": 106}
] 

#or you can import the file with all pokemone 
#from pokedex import POKEDEX  # ← import from your existing pokedex file
#pokemon = POKEDEX  # ← just point pokemon to your existing POKEDEX list