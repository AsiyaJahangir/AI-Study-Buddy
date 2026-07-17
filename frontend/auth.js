const BACKEND_URL = "https://humble-broccoli-77vg4wwgxgpw2rpv-5000.app.github.dev";

function showTab(tab) {
  document.getElementById("login-tab").classList.toggle("active", tab === "login");
  document.getElementById("register-tab").classList.toggle("active", tab === "register");
  document.getElementById("login-form").style.display = tab === "login" ? "block" : "none";
  document.getElementById("register-form").style.display = tab === "register" ? "block" : "none";
}

async function handleLogin() {
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value;
  const errorBox = document.getElementById("login-error");
  errorBox.innerText = "";

  if (!username || !password) {
    errorBox.innerText = "Please fill in both fields.";
    return;
  }

  try {
    const response = await fetch(`${BACKEND_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await response.json();

    if (data.success) {
      localStorage.setItem("token", data.token);
      localStorage.setItem("username", data.username);
      window.location.href = "index.html";
    } else {
      errorBox.innerText = data.error || "Login failed.";
    }
  } catch (err) {
    errorBox.innerText = "Couldn't reach the server.";
  }
}

async function handleRegister() {
  const username = document.getElementById("register-username").value.trim();
  const password = document.getElementById("register-password").value;
  const errorBox = document.getElementById("register-error");
  errorBox.innerText = "";

  if (!username || !password) {
    errorBox.innerText = "Please fill in both fields.";
    return;
  }
  if (password.length < 4) {
    errorBox.innerText = "Password should be at least 4 characters.";
    return;
  }

  try {
    const response = await fetch(`${BACKEND_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await response.json();

    if (data.success) {
      errorBox.style.color = "#2e7d32";
      errorBox.innerText = "Account created! You can now log in.";
      showTab("login");
    } else {
      errorBox.innerText = data.error || "Registration failed.";
    }
  } catch (err) {
    errorBox.innerText = "Couldn't reach the server.";
  }
}