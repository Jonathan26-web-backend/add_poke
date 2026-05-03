const API = "http://localhost:5000/api";
let token = null;  // stores the JWT token in memory

document.addEventListener("DOMContentLoaded", init);

function init() {
    // attach click listeners to all buttons
    document.querySelector("#loginBtn").addEventListener("click", login);
    document.querySelector("#logoutBtn").addEventListener("click", logout);
    document.querySelector("#loadPokemonBtn").addEventListener("click", loadPokemon);
    document.querySelector("#searchBtn").addEventListener("click", searchPokemon);
    document.querySelector("#addBtn").addEventListener("click", addPokemon);
    document.querySelector("#deleteBtn").addEventListener("click", deletePokemon);

    // restore token if user was already logged in
    token = localStorage.getItem("token");
    if (token) {
        document.querySelector("#loginStatus").innerText = "Already logged in.";
    }
}

// ---------------------
// LOGIN
// sends username + password, gets JWT token back
// ---------------------
async function login() {
    const username = document.querySelector("#username").value;
    const password = document.querySelector("#password").value;

    const response = await fetch(API + "/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (data.token) {
        token = data.token;
        localStorage.setItem("token", token);  // save token for page refresh
        document.querySelector("#loginStatus").innerText = "Logged in!";
    } else {
        document.querySelector("#loginStatus").innerText = "Login failed.";
    }
}

// ---------------------
// LOGOUT
// sends token to backend to invalidate it, clears local storage
// ---------------------
async function logout() {
    if (!token) {
        alert("Not logged in!");
        return;
    }

    await fetch(API + "/logout", {
        method: "POST",
        headers: { "Authorization": "Bearer " + token }  // send token to invalidate
    });
    // step 2 - clear token from memory
    token = null;
    localStorage.removeItem("token");  // remove from local storage
    document.querySelector("#loginStatus").innerText = "Logged out."; // clear status text
    document.querySelector("#pokemonList").innerHTML = ""; // clear pokemon list

    //this wasnt asked but i did it to clear out all input fields

    // clear all input fields ← new
    document.querySelector("#username").value = "";
    document.querySelector("#password").value = "";
    document.querySelector("#searchName").value = "";
    document.querySelector("#addName").value = "";
    document.querySelector("#addType").value = "";
    document.querySelector("#addHp").value = "";
    document.querySelector("#deleteId").value = "";
}

// ---------------------
// LOAD ALL POKEMON
// requires auth - sends token in Authorization header
// ---------------------
async function loadPokemon() {
    if (!token) {
        alert("Login first!");
        return;
    }

    const response = await fetch(API + "/pokemon", {
        method: "GET",
        headers: { "Authorization": "Bearer " + token }  // ← JWT token here
    });

    if (!response.ok) {
        document.querySelector("#pokemonStatus").innerText = "Failed to load pokemon.";
        return;
    }

    const data = await response.json();
    const list = document.querySelector("#pokemonList");
    list.innerHTML = "";

    data.forEach((p) => {
        const li = document.createElement("li");
        li.textContent = `${p.id} ${p.name}  ${p.type} ${p.hp}`;
        list.appendChild(li);
    });
}

// ---------------------
// SEARCH POKEMON by name
// uses query parameter: /api/pokemon/search?name=pikachu
// ---------------------
async function searchPokemon() {
    if (!token) {
        alert("Login first!");
        return;
    }

    const name = document.querySelector("#searchName").value;

    const response = await fetch(API + "/pokemon/search?name=" + name, {
        method: "GET",
        headers: { "Authorization": "Bearer " + token }
    });

    const data = await response.json();

    if (response.ok) {
        // found - display the pokemon
        document.querySelector("#searchResult").innerText =
            `Found: ${data.id} ${data.name} - Type: ${data.type} - HP: ${data.hp}`;
    } else {
        // not found
        document.querySelector("#searchResult").innerText = "Pokemon not found.";
    }
}

// ---------------------
// ADD POKEMON
// only works for admin and editor roles
// viewer will get 403 Forbidden from backend
// ---------------------
async function addPokemon() {
    if (!token) {
        alert("Login first!");
        return;
    }

    const name = document.querySelector("#addName").value;
    const type = document.querySelector("#addType").value;
    const hp = parseInt(document.querySelector("#addHp").value);

    const response = await fetch(API + "/pokemon", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token  // ← JWT token here
        },
        body: JSON.stringify({ name, type, hp })
    });

    if (response.status === 201) {
        document.querySelector("#addStatus").innerText = "Pokemon added!";
        loadPokemon();  // refresh the list
    } else if (response.status === 403) {
        document.querySelector("#addStatus").innerText = "No permission! Viewers cannot add pokemon.";
    } else {
        document.querySelector("#addStatus").innerText = "Failed to add pokemon.";
    }
}

// ---------------------
// DELETE POKEMON
// only works for admin role
// editor and viewer will get 403 Forbidden from backend
// ---------------------
async function deletePokemon() {
    if (!token) {
        alert("Login first!");
        return;
    }

    const id = document.querySelector("#deleteId").value;

    const response = await fetch(API + "/pokemon/" + id, {
        method: "DELETE",
        headers: { "Authorization": "Bearer " + token }  // ← JWT token here
    });

    if (response.status === 204) {
        document.querySelector("#deleteStatus").innerText = "Pokemon deleted!";
        loadPokemon();  // refresh the list
    } else if (response.status === 403) {
        document.querySelector("#deleteStatus").innerText = "No permission! Only admin can delete.";
    } else {
        document.querySelector("#deleteStatus").innerText = "Failed to delete pokemon.";
    }
}