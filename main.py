from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from transformers import pipeline

app = FastAPI()

# Load the pre-trained model for conversational AI
chatbot = pipeline(model="facebook/blenderbot-400M-distill")

# HTML page to serve
index_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>AI Chatbot</title>
    </head>
    <body>
        <h1>AI Chatbot</h1>
        <div id="chat-box"></div>
        <input type="text" id="user-input" placeholder="Type your message...">
        <button onclick="sendMessage()">Send</button>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var chatBox = document.getElementById("chat-box");
                var messageDiv = document.createElement("div");
                messageDiv.innerText = event.data;
                chatBox.appendChild(messageDiv);
            };
            function sendMessage() {
                var userInput = document.getElementById("user-input").value;
                ws.send(userInput);
                var chatBox = document.getElementById("chat-box");
                var messageDiv = document.createElement("div");
                messageDiv.innerText = userInput;
                messageDiv.style.textAlign = "right";
                chatBox.appendChild(messageDiv);
                document.getElementById("user-input").value = "";
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(content=index_html, status_code=200)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response = chatbot(data)
        await websocket.send_text(response[-1]['generated_text'])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
