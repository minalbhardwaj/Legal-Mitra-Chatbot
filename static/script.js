let messageInput = document.getElementById("message");
let chatBox = document.getElementById("chat-box");
let chatHistory = [];
let chatTitles = [];
let currentChat = [];



document.getElementById("send-btn").addEventListener("click", sendMessage);


function generateBotReply(userMsg) {
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMsg })
  })
  .then(response => response.json())
  .then(data => {
    if (data.html) {
      const wrapper = document.createElement("div");
      wrapper.innerHTML = data.html;
      chatBox.appendChild(wrapper);
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  });
}

document.getElementById("message").addEventListener("keypress", function(e) {
  if (e.key === "Enter") {
      sendMessage()
  }
});


function sendMessage() {
  const message = messageInput.value.trim();
  if (message === "") return;
  appendMessage("user", message);
  messageInput.value = "";
  generateBotReply(message);
}



function appendMessage(sender, message) {
  const msgDiv = document.createElement("div");
  msgDiv.className = sender === "user" ? "user-msg" : "bot-msg";

  const avatar = document.createElement("img");
  avatar.src = sender === "user"
    ? "https://cdn-icons-png.flaticon.com/128/2215/2215557.png" 
    : "https://cdn-icons-png.flaticon.com/64/6873/6873405.png"; 
  avatar.alt = sender;

  const bubble = document.createElement("div");
  bubble.innerText = message;

  msgDiv.appendChild(avatar);
  msgDiv.appendChild(bubble);
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  currentChat.push({ sender, message });
}





function startNewChat() {
  fetch("/new_conversation", { method: "POST" })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();  // reload to refresh previous conversations
        }
    });
  currentChat = [];
  chatBox.innerHTML = "";
}

function exportChat() {
  let text = currentChat.map(m => `${m.sender}: ${m.message}`).join("\n");
  let blob = new Blob([text], { type: "text/plain" });
  let link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "chat.txt";
  link.click();
}

function openHistory() {
  const modal = document.getElementById("historyModal");
  modal.classList.remove("hidden");
}

function closeHistory() {
  document.getElementById("historyModal").classList.add("hidden");
}



function startVoiceInput() {
  if (!("webkitSpeechRecognition" in window)) return alert("Speech recognition not supported");

  const recognition = new webkitSpeechRecognition();
  recognition.continuous = false;   
  recognition.interimResults = true;
  recognition.lang = "en-US";

  recognition.onresult = function (event) {
    const result = event.results[0];
    if (result.isFinal) {
      messageInput.value = result[0].transcript;
      sendMessage();
    } else {
      messageInput.value = result[0].transcript;
    }
  };

  recognition.start();
}

// function load_msg(id){
//   alert(id)
// }