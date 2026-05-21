const API_URL = "https://fastapi-task-manager-rxqc.onrender.com";

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (token) {
        showTasksUI();
    } else {
        showAuthUI();
    }
});

function showTasksUI() {
    document.getElementById("auth-section").style.display = "none";
    document.getElementById("task-section").style.display = "block";
    document.getElementById("user-display").innerText = localStorage.getItem("username") || "User";
    loadTasks();
}

function showAuthUI() {
    document.getElementById("auth-section").style.display = "block";
    document.getElementById("task-section").style.display = "none";
    localStorage.clear();
}

// 1. REGISTRATION FLOW
async function handleRegister() {
    const usernameInput = document.getElementById("username").value.trim();
    const passwordInput = document.getElementById("password").value.trim();

    if (!usernameInput || !passwordInput) {
        alert("Please enter both a username and a password to register.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: usernameInput, password: passwordInput })
        });

        const data = await response.json();
        
        if (response.ok) {
            alert("Registration successful! Please login with your details.");
        } else {
            alert("Registration Rejected: " + (data.detail || JSON.stringify(data.detail)));
        }
    } catch (err) {
        console.error("Network Exception:", err);
        alert("Cannot connect to backend server. Ensure Uvicorn is running.");
    }
}

// 2. LOGIN FLOW
async function handleLogin() {
    const usernameInput = document.getElementById("username").value.trim();
    const passwordInput = document.getElementById("password").value.trim();

    if (!usernameInput || !passwordInput) {
        alert("Please enter both a username and a password to login.");
        return;
    }

    // Must be encoded as x-www-form-urlencoded for OAuth2 password spec
    const bodyForm = new URLSearchParams();
    bodyForm.append("username", usernameInput);
    bodyForm.append("password", passwordInput);

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: bodyForm
        });

        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("username", usernameInput);
            showTasksUI();
        } else {
            alert("Login Failed: " + (data.detail || "Invalid Credentials"));
        }
    } catch (err) {
        console.error("Network Exception:", err);
        alert("Cannot connect to backend server.");
    }
}

// 3. LOGOUT FLOW
function handleLogout() {
    showAuthUI();
}

// 4. FETCH AND RENDER TASKS
async function loadTasks() {
    const token = localStorage.getItem("token");
    const filter = document.getElementById("filter-status").value;
    
    let targetUrl = `${API_URL}/tasks`;
    if (filter === "completed") targetUrl += "?completed=true";
    if (filter === "pending") targetUrl += "?completed=false";

    try {
        const response = await fetch(targetUrl, {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) {
            showAuthUI();
            return;
        }

        const tasks = await response.json();
        const taskListContainer = document.getElementById("task-list");
        taskListContainer.innerHTML = "";

        tasks.forEach(task => {
            const li = document.createElement("li");
            if (task.completed) li.classList.add("is-completed");

            li.innerHTML = `
                <div class="task-text">
                    <strong>${task.title}</strong><br>
                    <small>${task.description || 'No description provided.'}</small>
                </div>
                <div>
                    ${!task.completed ? `<button onclick="toggleTask(${task.id})" class="btn-success">Complete</button>` : ''}
                    <button onclick="deleteTask(${task.id})" class="btn-danger">Delete</button>
                </div>
            `;
            taskListContainer.appendChild(li);
        });
    } catch (err) {
        console.error("Task Loading Failed:", err);
    }
}

// 5. CREATE TASK
async function handleCreateTask() {
    const title = document.getElementById("task-title").value.trim();
    const description = document.getElementById("task-desc").value.trim();
    const token = localStorage.getItem("token");

    if (!title) {
        alert("Task title is required.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/tasks`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ title, description, completed: false })
        });

        if (response.ok) {
            document.getElementById("task-title").value = "";
            document.getElementById("task-desc").value = "";
            loadTasks();
        }
    } catch (err) {
        console.error("Task Creation Failed:", err);
    }
}

// 6. TOGGLE STATUS (PUT)
async function toggleTask(id) {
    const token = localStorage.getItem("token");
    try {
        await fetch(`${API_URL}/tasks/${id}`, {
            method: "PUT",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ completed: true })
        });
        loadTasks();
    } catch (err) {
        console.error("Task Toggle Failed:", err);
    }
}

// 7. DELETE TASK
async function deleteTask(id) {
    const token = localStorage.getItem("token");
    try {
        await fetch(`${API_URL}/tasks/${id}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });
        loadTasks();
    } catch (err) {
        console.error("Task Deletion Failed:", err);
    }
}