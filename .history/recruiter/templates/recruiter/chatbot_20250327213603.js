<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .chatbot-icon {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #007bff;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        }
        .chatbox {
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 300px;
            height: 400px;
            background: white;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
            display: none;
            flex-direction: column;
        }
        .chat-header {
            background-color: #007bff;
            color: white;
            padding: 10px;
            text-align: center;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
        .chat-messages {
            flex: 1;
            padding: 10px;
            overflow-y: auto;
            font-size: 14px;
        }
        .chat-input {
            display: flex;
            padding: 10px;
        }
        .chat-input input {
            flex: 1;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .chat-input button {
            background: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            margin-left: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="chatbot-icon" onclick="toggleChat()">💬</div>
    <div class="chatbox" id="chatbox">
        <div class="chat-header">Job & HR Assistant</div>
        <div class="chat-messages" id="chat-messages"></div>
        <div class="chat-input">
            <input type="text" id="user-input" placeholder="Ask about jobs, hiring...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        function toggleChat() {
            const chatbox = document.getElementById("chatbox");
            chatbox.style.display = chatbox.style.display === "none" ? "flex" : "none";
        }

        async function sendMessage() {
            const input = document.getElementById("user-input");
            const messages = document.getElementById("chat-messages");
            if (input.value.trim() === "") return;

            const userMessage = `<div><strong>You:</strong> ${input.value}</div>`;
            messages.innerHTML += userMessage;
            const userQuery = input.value;
            input.value = "";
            messages.scrollTop = messages.scrollHeight;

            // Call Gemini API (Replace with actual API call)
            const botResponse = await getBotResponse(userQuery);
            messages.innerHTML += `<div><strong>Bot:</strong> ${botResponse}</div>`;
            messages.scrollTop = messages.scrollHeight;
        }

        async function getBotResponse(query) {
            const apiKey = "AIzaSyAe-FXs98VsjnnNSv-qKCBWNZeD1Boi2Zc";
            const response = await fetch("https://api.gemini.com/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json", "Authorization": `Bearer ${apiKey}` },
                body: JSON.stringify({ query: query })
            });
            const data = await response.json();
            return data.response || "Sorry, I couldn't understand that.";
        }
    </script>
</body>
</html>
