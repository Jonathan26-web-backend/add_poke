const API = "http://localhost:5000/api";
let apiKey = null;

document.addEventListener("DOMContentLoaded", init);

function init() {
    //fetc all the btn
    document.querySelector("#loginBtn").addEventListener("click", login);
    document.querySelector("#logoutBtn").addEventListener("click", logout);
    document.querySelector("#loadMoviesBtn").addEventListener("click", loadMissions);

    // restore key if already logged in
    apiKey = localStorage.getItem("apiKey");
    if (apiKey) {
        document.querySelector("#loginStatus").innerText = "You have successfully logged in.";
    }
}

// LOGIN
async function login() {
    const username = document.querySelector("#username").value;
    const password = document.querySelector("#password").value;

    const response = await fetch(API + "/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (data.api_key) {
        apiKey = data.api_key;
        localStorage.setItem("apiKey", apiKey);
        document.querySelector("#loginStatus").innerText = "Logged in!";
    } else {
        document.querySelector("#loginStatus").innerText = "Login failed.";
    }
}

// LOGOUT
function logout() {
    apiKey = null;
    localStorage.removeItem("apiKey");
    document.querySelector("#loginStatus").innerText = "Logged out.";
    document.querySelector("#missions").innerHTML = "";
}

// LOAD MISSIONS
async function loadMissions() {
    if (!apiKey) {
        alert("Login first!");
        return;
    }

    const response = await fetch(API + "/missions", {
        method: "GET",
        headers: { "Authorization": apiKey }  // ← send API key in header
    });

    if (!response.ok) {
        document.querySelector("#missionStatus").innerText = "Failed to load missions.";
        return;
    }

    const data = await response.json();
    const list = document.querySelector("#missions");
    list.innerHTML = "";

    data.forEach((mission) => {
        const li = document.createElement("li");
        li.textContent = `${mission.id} - ${mission.mission}`;
        list.appendChild(li);
    });
}