const BACKEND_URL = "https://humble-broccoli-77vg4wwgxgpw2rpv-5000.app.github.dev";

let currentChatId = null;
const token = localStorage.getItem("token");
const username = localStorage.getItem("username");

// ---------- Auth guard ----------
if (!token) {
  window.location.href = "login.html";
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("username-display").innerText = "👤 " + username;
  startNewChat();
});

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token
  };
}

function handleLogout() {
  localStorage.removeItem("token");
  localStorage.removeItem("username");
  window.location.href = "login.html";
}

// ---------- Chat list (sidebar) ----------
async function loadChatList() {
  try {
    const res = await fetch(`${BACKEND_URL}/chats`, { headers: authHeaders() });
    if (res.status === 401) { handleLogout(); return; }
    const data = await res.json();
    renderChatList(data.chats);
  } catch (err) {
    console.error("Couldn't load chats", err);
  }
}

function renderChatList(chats) {
  const list = document.getElementById("chat-list");
  list.innerHTML = "";
  chats.forEach(chat => {
    const item = document.createElement("div");
    item.className = "chat-item" + (chat.id === currentChatId ? " active" : "");
    item.innerHTML = `<span onclick="selectChat(${chat.id})">${chat.title || "New Chat"}</span><span class="delete-x" onclick="deleteChat(${chat.id}, event)">✕</span>`;
    list.appendChild(item);
  });
}

async function startNewChat() {
  const res = await fetch(`${BACKEND_URL}/chats`, { method: "POST", headers: authHeaders() });
  const data = await res.json();
  currentChatId = data.chat_id;
  document.getElementById("messages-panel").innerHTML = "";
  document.getElementById("notes-input").value = "";
  loadChatList();
}

async function selectChat(chatId) {
  currentChatId = chatId;
  const res = await fetch(`${BACKEND_URL}/chats/${chatId}/messages`, { headers: authHeaders() });
  const data = await res.json();
  renderMessages(data.messages);
  loadChatList();
}

async function deleteChat(chatId, event) {
  event.stopPropagation();
  if (!confirm("Delete this chat? This can't be undone.")) return;
  await fetch(`${BACKEND_URL}/chats/${chatId}`, { method: "DELETE", headers: authHeaders() });
  if (chatId === currentChatId) currentChatId = null;
  loadChatList();
}

async function clearAllChats() {
  if (!confirm("Delete ALL your chats? This can't be undone.")) return;
  await fetch(`${BACKEND_URL}/chats/clear`, { method: "DELETE", headers: authHeaders() });
  currentChatId = null;
  document.getElementById("messages-panel").innerHTML = "";
  loadChatList();
}

function renderMessages(messages) {
  const panel = document.getElementById("messages-panel");
  panel.innerHTML = "";
  messages.forEach(msg => {
    if (msg.role !== "assistant") return;

    if (msg.content.startsWith("[CHART]")) {
      const chartData = JSON.parse(msg.content.replace("[CHART]", ""));
      addChartBlock(chartData);
    } else {
      const block = document.createElement("div");
      block.className = "msg-block";
      block.innerHTML = `<div class="msg-header">🤖 Result</div><div class="msg-content">${msg.content}</div>`;
      panel.appendChild(block);
    }
  });
}

let mermaidInitialized = false;

function initMermaidOnce() {
  if (!mermaidInitialized) {
    mermaid.initialize({ startOnLoad: false, theme: "base", themeVariables: {
      primaryColor: "#f3ebff", primaryBorderColor: "#7c3aed", lineColor: "#7c3aed",
      primaryTextColor: "#1a1a2e"
    }});
    mermaidInitialized = true;
  }
}

function addChartBlock(data) {
  const panel = document.getElementById("messages-panel");
  const block = document.createElement("div");
  block.className = "msg-block";
  const uid = "viz-" + Date.now() + Math.random().toString(36).slice(2);

  if (data.type === "flowchart") {
    block.innerHTML = `<div class="msg-header">🔀 ${data.title || "Flowchart"}</div><div class="msg-content"><div class="mermaid" id="${uid}">${data.mermaid}</div></div>`;
    panel.appendChild(block);
    initMermaidOnce();
    mermaid.run({ nodes: [document.getElementById(uid)] });
  } else {
    const chartType = data.chart_type || "bar";
    block.innerHTML = `<div class="msg-header">📊 ${data.title || "Chart"}</div><div class="msg-content"><canvas id="${uid}" height="180"></canvas></div>`;
    panel.appendChild(block);

    new Chart(document.getElementById(uid), {
      type: chartType,
      data: {
        labels: data.labels,
        datasets: [{
          label: data.title || "Value",
          data: data.values,
          backgroundColor: chartType === "pie"
            ? ["#7c3aed", "#c026d3", "#0891b2", "#ea580c", "#16a34a", "#eab308"]
            : "#8e5fd6",
          borderRadius: chartType === "bar" ? 8 : 0,
          borderColor: "#7c3aed",
          fill: chartType === "line" ? false : true
        }]
      },
      options: {
        plugins: { legend: { display: chartType === "pie" } },
        scales: chartType === "pie" ? {} : { y: { beginAtZero: true } }
      }
    });
  }
}
async function handleVisualize() {
  const notes = document.getElementById("notes-input").value.trim();
  const loading = document.getElementById("loading");

  if (!notes) {
    alert("Please paste some notes first!");
    return;
  }
  if (!currentChatId) {
    await startNewChat();
  }

  loading.style.display = "flex";

  try {
    const response = await fetch(BACKEND_URL + "/visualize", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ notes: notes, chat_id: currentChatId })
    });
    const data = await response.json();

    if (data.chart) {
      addChartBlock(data.chart);
    } else {
      const panel = document.getElementById("messages-panel");
      const block = document.createElement("div");
      block.className = "msg-block";
      block.innerHTML = `<div class="msg-header">📊 Visualize</div><div class="msg-content">${data.message}</div>`;
      panel.appendChild(block);
    }
  } catch (err) {
    alert("Couldn't reach the server.");
  }

  loading.style.display = "none";
}


// ---------- AI actions ----------
async function handleAction(type) {
  const notes = document.getElementById("notes-input").value.trim();
  const loading = document.getElementById("loading");

  if (!notes) {
    alert("Please paste some notes first!");
    return;
  }
  if (!currentChatId) {
    await startNewChat();
  }

  loading.style.display = "flex";

  const endpoint = type === "summarize" ? "/summarize" : "/quiz";

  try {
    const response = await fetch(BACKEND_URL + endpoint, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ notes: notes, chat_id: currentChatId })
    });
    const data = await response.json();

    const panel = document.getElementById("messages-panel");
    const block = document.createElement("div");
    block.className = "msg-block";
    const label = type === "summarize" ? "📝 Summary" : "❓ Quiz Questions";
    block.innerHTML = `<div class="msg-header">${label}</div><div class="msg-content">${data.result}</div>`;
    panel.appendChild(block);

    loadChatList();
  } catch (err) {
    alert("Couldn't reach the server. Check your connection.");
  }

  loading.style.display = "none";
}